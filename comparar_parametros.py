"""
Experimento extra: efeito da taxa de mutação e do tamanho da população.
Usa o círculo (que tem ótimo conhecido) e repete cada configuração com 10 seeds,
porque uma única execução de um algoritmo genético pode ter sorte ou azar.
Rodar com: python comparar_parametros.py
"""
import random

import algoritmo_genetico as ag

PONTOS = 20
RAIO = 40
TAXA_SELECAO = 0.5
MAX_GERACOES = 500
MAX_ESTAGNACAO = 100
SEEDS = range(10)

TAXAS_MUTACAO = [0.0, 0.01, 0.05, 0.20, 0.50, 1.0]
TAMANHOS_POPULACAO = [20, 50, 100, 200, 500]
POPULACAO_PADRAO = 100
MUTACAO_PADRAO = 0.05

pontos = ag.gerar_pontos_circulo(PONTOS, RAIO)
otimo = ag.distancia_otima_circulo(PONTOS, RAIO)


def testar(tamanho_populacao, taxa_mutacao):
    soma_erros = 0
    soma_epocas = 0
    soma_tempos = 0
    acertos = 0

    for seed in SEEDS:
        random.seed(seed)
        historico = ag.executar_algoritmo_genetico(
            pontos, tamanho_populacao, TAXA_SELECAO, taxa_mutacao,
            MAX_GERACOES, MAX_ESTAGNACAO, mostrar_progresso=False)

        erro = (historico["melhores"][-1] - otimo) / otimo * 100
        soma_erros += erro
        soma_epocas += len(historico["melhores"]) - 1
        soma_tempos += historico["tempo_total"]
        if erro < 0.01:
            acertos += 1

    n = len(SEEDS)
    print(f"| {tamanho_populacao} | {taxa_mutacao:.0%} | {acertos}/{n} | {soma_erros / n:.2f}% | "
          f"{soma_epocas / n:.0f} | {soma_tempos / n:.3f} s |")


print(f"Círculo com {PONTOS} pontos, {len(SEEDS)} seeds por configuração")
cabecalho = "| População | Mutação | Achou o ótimo | Erro médio | Épocas (média) | Tempo (média) |"

print("\nVariando a taxa de mutação:\n")
print(cabecalho)
print("|---|---|---|---|---|---|")
for taxa in TAXAS_MUTACAO:
    testar(POPULACAO_PADRAO, taxa)

print("\nVariando o tamanho da população:\n")
print(cabecalho)
print("|---|---|---|---|---|---|")
for tamanho in TAMANHOS_POPULACAO:
    testar(tamanho, MUTACAO_PADRAO)
