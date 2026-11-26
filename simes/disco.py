# -*- coding: utf-8 -*-
"""
Modelos de dispositivo de armazenamento.

DiscoHDD  — FORNECIDO. Implementa o modelo de custo descrito em parametros.py.
DiscoFlash — BÔNUS. Armazenamento flash (SSD, celulares): implementem se quiserem o bônus.

Todo dispositivo oferece:
    atender(bloco, n_blocos, tipo) -> (duracao_ms, distancia_cilindros)
    mover(cilindro)                -> (duracao_ms, distancia_cilindros)
    cilindro_atual                 (atributo)
"""
from simes import parametros as P
from collections import deque
import math


def cilindro_do_bloco(bloco):
    return bloco // P.BLOCOS_POR_CILINDRO


class DiscoHDD:
    nome = "hdd"

    def __init__(self, busca_minima_ms=P.BUSCA_MINIMA_MS,
                 busca_por_cilindro_ms=P.BUSCA_POR_CILINDRO_MS,
                 latencia_rotacional_ms=P.LATENCIA_ROTACIONAL_MS,
                 transferencia_ms_por_bloco=P.TRANSFERENCIA_MS_POR_BLOCO,
                 cilindros=P.CILINDROS, cilindro_inicial=0, nome=None):
        self.busca_minima_ms = busca_minima_ms
        self.busca_por_cilindro_ms = busca_por_cilindro_ms
        self.latencia_rotacional_ms = latencia_rotacional_ms
        self.transferencia_ms_por_bloco = transferencia_ms_por_bloco
        self.cilindros = cilindros
        self.cilindro_atual = cilindro_inicial
        self.ultimo_bloco = None          # último bloco transferido (para detectar sequência)
        self.deslocamento_total = 0       # cilindros percorridos pelo braço
        if nome:
            self.nome = nome

    def tempo_busca(self, distancia):
        if distancia == 0:
            return 0.0
        return self.busca_minima_ms + distancia * self.busca_por_cilindro_ms

    def mover(self, cilindro):
        """Leva o braço até um cilindro sem transferir dados (usado pelo SCAN e pelo C-SCAN)."""
        distancia = abs(cilindro - self.cilindro_atual)
        duracao = self.tempo_busca(distancia)
        self.cilindro_atual = cilindro
        self.ultimo_bloco = None
        self.deslocamento_total += distancia
        return duracao, distancia

    def atender(self, bloco, n_blocos=1, tipo="L"):
        cilindro = cilindro_do_bloco(bloco)
        distancia = abs(cilindro - self.cilindro_atual)
        duracao = self.tempo_busca(distancia)
        em_sequencia = self.ultimo_bloco is not None and bloco == self.ultimo_bloco + 1
        if not em_sequencia:
            duracao += self.latencia_rotacional_ms
        duracao += n_blocos * self.transferencia_ms_por_bloco
        ultimo = bloco + n_blocos - 1
        self.cilindro_atual = cilindro_do_bloco(ultimo)
        self.ultimo_bloco = ultimo
        self.deslocamento_total += distancia
        return duracao, distancia


def criar_disco(nome):
    """Fábrica usada pelos simuladores e pelos experimentos."""
    if nome == "hdd":
        return DiscoHDD()
    if nome == "rapido":
        return DiscoHDD(nome="rapido", **P.DISPOSITIVO_RAPIDO)
    if nome == "flash":
        return DiscoFlash()
    raise ValueError("dispositivo desconhecido: %s" % nome)


# ======================================================================
# BÔNUS — armazenamento flash
# ======================================================================
class DiscoFlash:
    """
    Simula um SSD com uma camada de tradução simples (FTL) do tipo log:

    - uma página flash = um bloco lógico de 4 KiB;
    - páginas são agrupadas em blocos apagáveis de FLASH_PAGINAS_POR_BLOCO_APAGAVEL páginas;
    - uma página só pode ser gravada se estiver apagada; apagar só é possível por bloco inteiro;
    - regravar um bloco lógico grava em uma página livre nova e invalida a antiga;
    - quando faltam páginas livres, a coleta de lixo escolhe um bloco apagável, copia as
      páginas ainda válidas para outro lugar e apaga o bloco.

    Não há busca nem latência rotacional. Tempos em parametros.py (FLASH_*).
    Indicadores que o dispositivo deve expor (atributos):
        paginas_gravadas_host      páginas pedidas pelo sistema
        paginas_programadas        páginas efetivamente gravadas (inclui cópias da coleta de lixo)
        apagamentos                blocos apagados
    Amplificação de escrita = paginas_programadas / paginas_gravadas_host.
    """
    nome = "flash"

    def __init__(self, total_blocos_logicos=P.TOTAL_BLOCOS):
        if not isinstance(total_blocos_logicos, int) or total_blocos_logicos <= 0:
            raise ValueError("capacidade lógica deve ser positiva")
        self.cilindro_atual = 0
        self.cilindros = P.CILINDROS  # interface do simulador; flash não usa busca
        self.deslocamento_total = 0
        self.paginas_gravadas_host = 0
        self.paginas_programadas = 0
        self.apagamentos = 0
        self.total_blocos_logicos = total_blocos_logicos
        self.paginas_por_bloco = P.FLASH_PAGINAS_POR_BLOCO_APAGAVEL
        # Arredondamento por bloco; ao menos um bloco de reserva permite compactar.
        minimo = max(math.ceil(total_blocos_logicos * (1 + P.FLASH_AREA_RESERVA)),
                     total_blocos_logicos + self.paginas_por_bloco)
        self.total_paginas = ((minimo + self.paginas_por_bloco - 1)
                              // self.paginas_por_bloco * self.paginas_por_bloco)
        self.paginas = [-1] * self.total_paginas  # -1 apagada, -2 inválida, >=0 endereço lógico
        self.mapa = {}  # endereço lógico -> página física válida
        self.livres = deque(range(self.total_paginas))
        n = self.total_paginas // self.paginas_por_bloco
        self.validas = [0] * n
        self.invalidas = [0] * n
        self.apagadas = [self.paginas_por_bloco] * n

    def _invalidar(self, logico):
        antigo = self.mapa.pop(logico, None)
        if antigo is not None:
            b = antigo // self.paginas_por_bloco
            self.paginas[antigo] = -2
            self.validas[b] -= 1
            self.invalidas[b] += 1

    def _programar_pagina(self, logico):
        fisico = self.livres.popleft()
        if self.paginas[fisico] != -1:
            raise RuntimeError("tentativa de programar página não apagada")
        self._invalidar(logico)
        self.paginas[fisico] = logico
        self.mapa[logico] = fisico
        b = fisico // self.paginas_por_bloco
        self.validas[b] += 1
        self.apagadas[b] -= 1
        self.paginas_programadas += 1

    def _coletar(self):
        candidatos = [b for b in range(len(self.validas))
                      if self.invalidas[b] and
                      self.validas[b] <= len(self.livres) - self.apagadas[b]]
        if not candidatos:
            raise RuntimeError("sem bloco coletável com a reserva disponível")
        vitima = min(candidatos, key=lambda b: (-self.invalidas[b], self.validas[b], b))
        inicio = vitima * self.paginas_por_bloco
        fim = inicio + self.paginas_por_bloco
        sobreviventes = [l for l in self.paginas[inicio:fim] if l >= 0]
        # A cópia usa outro bloco; páginas apagadas da vítima não podem ser destino.
        self.livres = deque(p for p in self.livres if not inicio <= p < fim)
        for logico in sobreviventes:
            self._programar_pagina(logico)
        self.paginas[inicio:fim] = [-1] * self.paginas_por_bloco
        self.validas[vitima] = self.invalidas[vitima] = 0
        self.apagadas[vitima] = self.paginas_por_bloco
        self.livres.extend(range(inicio, fim))
        self.apagamentos += 1
        return (len(sobreviventes) * (P.FLASH_LEITURA_MS + P.FLASH_PROGRAMACAO_MS)
                + P.FLASH_APAGAMENTO_MS)

    def mover(self, cilindro):
        return 0.0, 0

    def atender(self, bloco, n_blocos=1, tipo="L"):
        if tipo not in ("L", "E") or not isinstance(bloco, int) or not isinstance(n_blocos, int):
            raise ValueError("requisição inválida")
        if bloco < 0 or n_blocos <= 0 or bloco + n_blocos > self.total_blocos_logicos:
            raise ValueError("requisição fora da área lógica")
        if tipo == "L":
            return n_blocos * P.FLASH_LEITURA_MS, 0
        duracao = 0.0
        for logico in range(bloco, bloco + n_blocos):
            self._invalidar(logico)
            if len(self.livres) <= self.paginas_por_bloco:
                duracao += self._coletar()
            self._programar_pagina(logico)
            self.paginas_gravadas_host += 1
            duracao += P.FLASH_PROGRAMACAO_MS
        return duracao, 0
