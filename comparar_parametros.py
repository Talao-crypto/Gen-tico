"""
Experimento extra: efeito da taxa de mutação e do tamanho da população.

Usa o benchmark do círculo (ótimo conhecido) e repete cada configuração com
várias seeds, porque uma única execução de um AG pode ter sorte ou azar.
Rodar com: python comparar_parametros.py
"""
import random

import algoritmo_genetico as ag
import main

SEEDS = range(10)
TAXAS_MUTACAO = [0.0, 0.01, 0.05, 0.20, 0.50, 1.0]
TAMANHOS_POPULACAO = [20, 50, 100, 200, 500]


def avaliar_configuracao(tamanho_populacao, taxa_mutacao):
    pontos = ag.gerar_pontos_circulo(main.N_POINTS_CIRCLE, main.CIRCLE_RADIUS)
    otima = ag.distancia_otima_circulo(main.N_POINTS_CIRCLE, main.CIRCLE_RADIUS)
    erros, epocas, tempos = [], [], []

    for seed in SEEDS:
        random.seed(seed)
        historico = ag.executar_algoritmo_genetico(
            pontos, tamanho_populacao, main.SELECTION_RATE, taxa_mutacao,
            main.MAX_GENERATIONS, main.MAX_STAGNATION, mostrar_progresso=False,
        )
        erros.append((historico["melhor_distancia"] - otima) / otima * 100)
        epocas.append(historico["total_epocas"])
        tempos.append(historico["tempo_total"])

    acertos = sum(1 for erro in erros if erro < 0.01)
    print(f"| {tamanho_populacao} | {taxa_mutacao:.0%} | {acertos}/{len(SEEDS)} | "
          f"{sum(erros) / len(erros):.2f}% | {sum(epocas) / len(epocas):.0f} | "
          f"{sum(tempos) / len(tempos):.3f} s |")


def imprimir_cabecalho():
    print("| População | Mutação | Achou o ótimo | Erro médio | Épocas (média) | Tempo (média) |")
    print("|---|---|---|---|---|---|")


if __name__ == "__main__":
    print(f"Círculo com {main.N_POINTS_CIRCLE} pontos, {len(SEEDS)} seeds por configuração\n")

    print("Variando a taxa de mutação:\n")
    imprimir_cabecalho()
    for taxa in TAXAS_MUTACAO:
        avaliar_configuracao(main.POPULATION_SIZE, taxa)

    print("\nVariando o tamanho da população:\n")
    imprimir_cabecalho()
    for tamanho in TAMANHOS_POPULACAO:
        avaliar_configuracao(tamanho, main.MUTATION_RATE)
