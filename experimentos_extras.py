"""Experimento suplementar de GC. Não altera as cargas nem os CSVs oficiais.

Executar: python3 experimentos_extras.py
"""
import csv
import os
import random

from simes.disco import DiscoFlash


def conferir_mapa(disco):
    if len(disco.mapa) != sum(disco.validas):
        raise AssertionError("contagem de páginas válidas inconsistente")
    if len(disco.livres) != sum(disco.apagadas):
        raise AssertionError("contagem de páginas apagadas inconsistente")
    if any(disco.paginas[p] != l for l, p in disco.mapa.items()):
        raise AssertionError("FTL não preservou uma página lógica")


def main():
    linhas = []
    for padrao in ("sequencial", "aleatoria"):
        logicos = 4096
        d = DiscoFlash(logicos)
        rng = random.Random(13)
        tempo = d.atender(0, logicos, "E")[0]
        for i in range(4 * logicos):
            alvo = i % logicos if padrao == "sequencial" else rng.randrange(logicos)
            tempo += d.atender(alvo, 1, "E")[0]
        conferir_mapa(d)
        linhas.append({
            "experimento": "EXTRA_FLASH_GC", "padrao": padrao, "semente": 13,
            "paginas_logicas": logicos, "paginas_fisicas": d.total_paginas,
            "reserva_efetiva_pct": 100 * (d.total_paginas / logicos - 1),
            "paginas_gravadas_host": d.paginas_gravadas_host,
            "paginas_programadas": d.paginas_programadas,
            "copias_gc": d.paginas_programadas - d.paginas_gravadas_host,
            "apagamentos": d.apagamentos,
            "amplificacao_escrita": d.paginas_programadas / d.paginas_gravadas_host,
            "tempo_total_ms": tempo,
            "paginas_logicas_preservadas": len(d.mapa),
        })
    pasta = os.path.join(os.path.dirname(os.path.abspath(__file__)), "resultados")
    os.makedirs(pasta, exist_ok=True)
    caminho = os.path.join(pasta, "extra_flash_gc.csv")
    with open(caminho, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(linhas[0]))
        w.writeheader()
        w.writerows(linhas)
    print("Experimento suplementar gravado em resultados/extra_flash_gc.csv")
    for linha in linhas:
        print(linha)


if __name__ == "__main__":
    main()
