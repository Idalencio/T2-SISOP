"""Casos de fronteira e invariantes além dos testes fornecidos pelo professor."""
import random
import unittest

from simes import parametros as P
from simes.arquivos.alocacao import AlocadorEncadeado, AlocadorFAT, AlocadorIndexado
from simes.arquivos.estruturas import ErroSA, FCB
from simes.arquivos.simulador import montar_sistema
from simes.disco import DiscoFlash
from simes.es.cache import CacheFIFO, CacheLRU
from simes.es.escalonadores import Deadline, SCAN, SSTF
from simes.es.requisicao import Requisicao
from simes.integracao import historico_para_requisicoes


class TesteFronteirasArquivos(unittest.TestCase):
    def setUp(self):
        self.sa = montar_sistema(total_blocos=100)
        self.sa.create("P1", "/f", P.TAMANHO_BLOCO)

    def test_unlink_espera_ultimo_de_tres_handles(self):
        sa = self.sa
        antes = sa.alocador.bitmap.livres()
        for proc, h in (("P1", "a"), ("P1", "b"), ("P2", "a")):
            sa.open(proc, "/f", "rw", h)
        sa.unlink("P1", "/f")
        sa.close("P1", "a")
        sa.close("P2", "a")
        self.assertEqual(sa.alocador.bitmap.livres(), antes)
        self.assertEqual(sa.read("P1", "b", 10), 10)
        sa.close("P1", "b")
        self.assertEqual(sa.alocador.bitmap.livres(), antes + 1)
        self.assertEqual(len(sa.tabela_global), 0)

    def test_append_recalcula_fim_apos_seek_e_outra_abertura(self):
        sa = self.sa
        sa.open("P1", "/f", "a", "a")
        sa.open("P2", "/f", "a", "a")
        sa.seek("P1", "a", 0)
        sa.write("P2", "a", 100)
        sa.write("P1", "a", 200)
        self.assertEqual(sa.resolver("/f").tamanho, P.TAMANHO_BLOCO + 300)

    def test_zero_bytes_e_eof_nao_movem_posicao_para_tras(self):
        sa = self.sa
        sa.open("P1", "/f", "rw", "h")
        sa.seek("P1", "h", 20000)
        antes = sa.camada.acessos
        self.assertEqual(sa.read("P1", "h", 10), 0)
        self.assertEqual(sa.write("P1", "h", 0), 0)
        self.assertEqual(sa.tabelas_processo["P1"]["h"].posicao, 20000)
        self.assertEqual(sa.camada.acessos, antes)
        self.assertEqual(sa.resolver("/f").tamanho, P.TAMANHO_BLOCO)

    def test_create_sem_espaco_nao_deixa_fcb_ou_entrada(self):
        antes = set(self.sa.fcbs)
        with self.assertRaises(ErroSA) as ctx:
            self.sa.create("P1", "/grande", 1000 * P.TAMANHO_BLOCO)
        self.assertEqual(ctx.exception.codigo, "ENOSPC")
        self.assertEqual(set(self.sa.fcbs), antes)
        self.assertNotIn("grande", self.sa.raiz.entradas)

    def test_handle_duplicado_nao_vaza_contador(self):
        self.sa.open("P1", "/f", "r", "h")
        with self.assertRaises(ErroSA):
            self.sa.open("P1", "/f", "r", "h")
        self.assertEqual(next(iter(self.sa.tabela_global.values())).contador, 1)


class TesteFronteirasAlocacao(unittest.TestCase):
    def test_indice_transicao_1024_1025_e_liberacao(self):
        a = AlocadorIndexado(1100)
        f = FCB(1, "f", "arquivo", 0)
        a.alocar(f, 1024)
        self.assertEqual(len(f.extra["indices"]), 1)
        a.estender(f, 1)
        self.assertEqual(len(f.extra["indices"]), 3)
        self.assertEqual(len(a.bloco_fisico(f, 1023)[1]), 2)
        self.assertEqual(len(a.bloco_fisico(f, 1024)[1]), 2)
        self.assertEqual(a.bitmap.ocupados, 1028)
        a.liberar(f)
        self.assertEqual(a.bitmap.ocupados, 0)

    def test_sem_espaco_extensao_e_atomica(self):
        for classe in (AlocadorEncadeado, AlocadorFAT, AlocadorIndexado):
            with self.subTest(alocador=classe.nome):
                a = classe(8)
                f = FCB(1, "f", "arquivo", 0)
                a.alocar(f, 4)
                antes = (list(f.blocos), bytes(a.bitmap.mapa), list(f.extra.get("indices", [])))
                with self.assertRaises(ErroSA):
                    a.estender(f, 10)
                self.assertEqual((f.blocos, bytes(a.bitmap.mapa), f.extra.get("indices", [])), antes)
                self.assertEqual(a.falhas, 1)

    def test_encadeada_retrocesso_paga_ponteiros(self):
        a = AlocadorEncadeado(20)
        f = FCB(1, "f", "arquivo", 0)
        a.alocar(f, 10)
        a.bloco_fisico(f, 8)
        self.assertEqual(len(a.bloco_fisico(f, 3)[1]), 3)
        self.assertEqual(a.bloco_fisico(f, 4)[1], [])


class TesteFronteirasES(unittest.TestCase):
    def test_cache_preserva_sujo_em_reinsercao_e_sync_nao_muda_ordem(self):
        for classe in (CacheLRU, CacheFIFO):
            c = classe(2)
            c.escrever(1)
            c.inserir(1)
            self.assertEqual(c.sujos(), 1)
            c.inserir(2)
            self.assertEqual(c.sincronizar(), [1])
            c.inserir(3)
            self.assertFalse(c.ler(1))

    def test_empates_e_mesmo_cilindro(self):
        reqs = [Requisicao(i, 0, "P", "L", b * 64) for i, b in enumerate((45, 55))]
        self.assertEqual(SSTF().escolher(reqs, 50, 1, 0, 4999)[0], 0)
        iguais = [Requisicao(0, 0, "P", "L", 50 * 64)]
        self.assertEqual(SCAN().escolher(iguais, 50, -1, 0, 4999), (0, -1, []))
        self.assertEqual(Deadline().escolher(reqs, 50, -1, 200, 4999), (0, -1, []))

    def test_integracao_preserva_ordem_dentro_de_um_instante(self):
        r = historico_para_requisicoes([(2, "P", "E", 9, 1), (1, "Q", "L", 4, 2),
                                       (2, "P", "L", 3, 1)])
        self.assertEqual([(x.id, x.bloco) for x in r], [(0, 4), (1, 9), (2, 3)])


class TesteFlash(unittest.TestCase):
    def conferir(self, d):
        self.assertEqual(sum(d.validas), len(d.mapa))
        self.assertEqual(sum(d.apagadas), len(d.livres))
        self.assertEqual(len(set(d.livres)), len(d.livres))
        self.assertEqual(sum(d.validas) + sum(d.invalidas) + sum(d.apagadas), d.total_paginas)
        for l, p in d.mapa.items():
            self.assertEqual(d.paginas[p], l)
        self.assertEqual(len({p for p in d.mapa.values()}), len(d.mapa))
        self.assertTrue(all(d.paginas[p] == -1 for p in d.livres))

    def test_custos_sem_coleta_e_limites(self):
        d = DiscoFlash(256)
        self.assertEqual(d.atender(0, 2, "L"), (2 * P.FLASH_LEITURA_MS, 0))
        self.assertEqual(d.atender(0, 2, "E"), (2 * P.FLASH_PROGRAMACAO_MS, 0))
        self.assertEqual((d.paginas_gravadas_host, d.paginas_programadas, d.apagamentos), (2, 2, 0))
        for bloco, n in ((-1, 1), (256, 1), (255, 2), (0, 0)):
            with self.assertRaises(ValueError):
                d.atender(bloco, n, "E")
        self.conferir(d)

    def test_coleta_preserva_mapa_e_cobra_copias(self):
        d = DiscoFlash(256)
        rng = random.Random(13)
        tempo = d.atender(0, 256, "E")[0]
        for i in range(1024):
            tempo += d.atender(rng.randrange(256), 1, "E")[0]
            if i % 100 == 0:
                self.conferir(d)
        self.conferir(d)
        self.assertEqual(len(d.mapa), 256)
        self.assertGreater(d.apagamentos, 0)
        self.assertGreater(d.paginas_programadas, d.paginas_gravadas_host)
        copias = d.paginas_programadas - d.paginas_gravadas_host
        esperado = (d.paginas_programadas * P.FLASH_PROGRAMACAO_MS
                    + copias * P.FLASH_LEITURA_MS + d.apagamentos * P.FLASH_APAGAMENTO_MS)
        self.assertAlmostEqual(tempo, esperado)


if __name__ == "__main__":
    unittest.main()
