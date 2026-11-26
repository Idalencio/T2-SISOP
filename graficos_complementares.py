"""Figuras adicionais para o relatório; preserva os gráficos oficiais."""
import csv
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

RAIZ = Path(__file__).resolve().parent
SAIDA = RAIZ / "graficos"
CORES = ["#183b5b", "#168b87", "#ea9b36", "#8277b5", "#c85165", "#688c45", "#5398c6"]


def ler(nome):
    with (RAIZ / "resultados" / nome).open(encoding="utf-8") as f:
        return list(csv.DictReader(f))


def salvar(fig, nome):
    fig.savefig(SAIDA / nome, dpi=180, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def main():
    SAIDA.mkdir(exist_ok=True)
    plt.rcParams.update({"font.size": 10, "axes.spines.top": False, "axes.spines.right": False,
                         "axes.titleweight": "bold", "axes.labelcolor": "#183b5b",
                         "text.color": "#183b5b", "axes.axisbelow": True})
    es, fs, ops = ler("es.csv"), ler("arquivos.csv"), ler("arquivos_por_operacao.csv")

    fig, ax = plt.subplots(figsize=(9, 3.3))
    cargas = ["sequencial", "aleatoria", "concentrada", "rajadas"]
    for i, esc in enumerate(("FCFS", "SSTF", "SCAN")):
        vals = [float(next(r["resposta_media_ms"] for r in es if r["experimento"] == "X1"
                           and r["carga"] == c and r["escalonador"] == esc)) for c in cargas]
        ax.bar(np.arange(4) + (i - 1) * .25, vals, .25, color=CORES[i], label=esc)
    ax.set_xticks(range(4), ["Sequencial\n(dois processos)", "Aleatória", "Concentrada", "Rajadas"])
    ax.set_ylabel("Resposta média (ms, log)"); ax.set_yscale("log")
    ax.grid(axis="y", alpha=.2); ax.legend(ncol=3, frameon=False)
    salvar(fig, "R_X1_resposta.png")

    fig, ax = plt.subplots(figsize=(9, 3.2))
    combos = [("hdd", "aleatoria"), ("hdd", "sequencial"), ("rapido", "aleatoria"), ("rapido", "sequencial")]
    for i, modo in enumerate(("polling", "interrupcao")):
        vals = [float(next(r["cpu_es_pct"] for r in es if r["experimento"] == "X2" and
                          (r["dispositivo"], r["carga"]) == c and r["modo_cpu"] == modo)) for c in combos]
        ax.bar(np.arange(4) + (i - .5) * .32, vals, .32, color=CORES[i], label=modo)
    ax.set_xticks(range(4), ["HDD\naleatória", "HDD\nsequencial", "Rápido\naleatória", "Rápido\nsequencial"])
    ax.set_yscale("log"); ax.set_ylabel("CPU de E/S (% do horizonte, log)")
    ax.legend(frameon=False); ax.grid(axis="y", alpha=.2)
    salvar(fig, "R_X2_cpu.png")

    fig, axes = plt.subplots(1, 2, figsize=(9, 3.0), layout="constrained")
    rr = [r for r in ops if r["experimento"] == "X4" and r["operacao"] == "open"]
    profundidades = [int(r["carga"].split("_")[1]) for r in rr]
    for ax, campo, ylabel in zip(axes, ("acessos_medios", "tempo_medio_ms"), ("Leituras por open (blocos)", "Tempo por open (ms)")):
        ax.plot(profundidades, [float(r[campo]) for r in rr], "o-", color=CORES[1])
        ax.set_xlabel("Profundidade (diretórios)"); ax.set_ylabel(ylabel)
        ax.set_xticks([1, 3, 5, 7, 10]); ax.grid(alpha=.2)
    salvar(fig, "R_X4_profundidade.png")

    fig, axes = plt.subplots(1, 2, figsize=(9, 3.3), layout="constrained")
    for i, politica in enumerate(("LRU", "FIFO")):
        rr = [r for r in es if r["experimento"] == "X6" and r["cache"] == politica and r["escrita"] == "write-back"]
        axes[0].plot([int(r["capacidade_cache"]) for r in rr], [float(r["acerto_cache_pct"]) for r in rr], "o-", color=CORES[i], label=politica)
    axes[0].set_xscale("log", base=2); axes[0].set_xticks([64, 256, 1024, 2048], ["64", "256", "1024", "2048"])
    axes[0].set_xlabel("Capacidade (blocos)"); axes[0].set_ylabel("Leituras com acerto (%)")
    for i, escrita in enumerate(("write-through", "write-back")):
        rr = [r for r in es if r["experimento"] == "X6" and r["cache"] == "LRU" and r["escrita"] == escrita]
        axes[1].plot([int(r["capacidade_cache"]) for r in rr], [float(r["resposta_media_ms"]) for r in rr], "o-", color=CORES[i], label=escrita)
    axes[1].set_xscale("log", base=2); axes[1].set_xticks([64, 256, 1024, 2048], ["64", "256", "1024", "2048"])
    axes[1].set_xlabel("Capacidade LRU (blocos)"); axes[1].set_ylabel("Resposta média (ms)")
    for ax in axes: ax.legend(frameon=False, fontsize=8); ax.grid(alpha=.2)
    salvar(fig, "R_X6_cache.png")

    fig, ax = plt.subplots(figsize=(9, 3.2))
    for i, esc in enumerate(("FCFS", "SSTF", "SCAN", "C-SCAN", "LOOK", "C-LOOK", "DEADLINE")):
        rr = [r for r in es if r["experimento"] == "X7" and r["escalonador"] == esc]
        ax.plot([1000 / float(r["intervalo_medio_ms"]) for r in rr], [float(r["espera_max_ms"]) for r in rr], "o-", color=CORES[i], label=esc)
    ax.set_xlabel("Taxa nominal de chegada (requisições/s)"); ax.set_ylabel("Maior espera (ms)")
    ax.grid(alpha=.2); ax.legend(ncol=4, frameon=False, fontsize=8)
    salvar(fig, "R_X7_espera.png")

    rr = [r for r in fs if r["experimento"] == "X11"]
    fig, axes = plt.subplots(1, 2, figsize=(9, 3.1), layout="constrained")
    for ax, campo, ylabel in zip(axes, ("acessos_por_op", "tempo_medio_op_ms"), ("Acessos por operação (blocos)", "Tempo médio por operação (ms)")):
        ax.bar([r["alocador"] for r in rr], [float(r[campo]) for r in rr], color=CORES[:4])
        ax.set_ylabel(ylabel); ax.grid(axis="y", alpha=.2)
    salvar(fig, "R_X11_alocacao.png")

    fig, axes = plt.subplots(1, 2, figsize=(9, 3.3), sharey=True, layout="constrained")
    for ax, carga in zip(axes, ("compilador", "banco_dados")):
        for i, esc in enumerate(("FCFS", "SSTF", "SCAN")):
            cenarios = [("contigua", "nenhuma"), ("contigua", "LRU"), ("indexada", "nenhuma"), ("indexada", "LRU")]
            vals = [float(next(r["resposta_media_ms"] for r in es if r["experimento"] == "X12" and r["carga"] == carga + "+" + a and r["cache"] == c and r["escalonador"] == esc)) for a, c in cenarios]
            ax.bar(np.arange(4) + (i - 1) * .25, vals, .25, color=CORES[i], label=esc)
        ax.set_xticks(range(4), ["Cont.\nsem", "Cont.\nLRU", "Índice\nsem", "Índice\nLRU"])
        ax.set_title("Compilador" if carga == "compilador" else "Banco de dados", fontsize=11)
        ax.set_yscale("log"); ax.grid(axis="y", alpha=.2); ax.legend(frameon=False, fontsize=7)
    axes[0].set_ylabel("Resposta por requisição (ms, log)")
    salvar(fig, "R_X12_integracao.png")

    rr = ler("extra_flash_gc.csv")
    fig, axes = plt.subplots(1, 2, figsize=(9, 2.8), layout="constrained")
    for ax, campo, ylabel in zip(axes, ("amplificacao_escrita", "tempo_total_ms"), ("Amplificação de escrita (vezes)", "Tempo total simulado (ms)")):
        ax.bar([r["padrao"] for r in rr], [float(r[campo]) for r in rr], color=CORES[:2])
        ax.set_ylabel(ylabel); ax.grid(axis="y", alpha=.2)
    salvar(fig, "R_X13_flash_gc.png")
    print("8 figuras complementares geradas em graficos/.")


if __name__ == "__main__":
    main()
