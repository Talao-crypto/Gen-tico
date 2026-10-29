"""
Experimento extra: efeito do tipo de mutação, da taxa de mutação e do tamanho da população.
Usa o círculo (que tem ótimo conhecido) e repete cada configuração com várias seeds,
porque uma única execução de um algoritmo genético pode ter sorte ou azar.

Rodar com:
    python comparar_parametros.py           # círculo de 20 pontos, 10 seeds (cerca de 1 minuto)
    python comparar_parametros.py --bonus   # também o círculo de 100 pontos, 3 seeds (cerca de 15 minutos)
"""
import random
import sys

import algoritmo_genetico as ag

RAIO = 40
TAXA_SELECAO = 0.5
POPULACAO_PADRAO = 100
MUTACAO_PADRAO = 0.05

# Círculo de 20 pontos (mesmos limites do main.py)
PONTOS = 20
MAX_GERACOES = 500
MAX_ESTAGNACAO = 100
SEEDS = range(10)
TAXAS_MUTACAO = [0.0, 0.01, 0.05, 0.20, 0.50, 1.0]
TAMANHOS_POPULACAO = [20, 50, 100, 200, 500]

# Círculo de 100 pontos (mesmos limites do bônus do main.py)
PONTOS_BONUS = 100
MAX_GERACOES_BONUS = 20000
MAX_ESTAGNACAO_BONUS = 2000
SEEDS_BONUS = range(3)
TAXAS_MUTACAO_BONUS = [0.02, 0.05, 0.10, 0.20]

CABECALHO = ("| Mutação | Taxa | População | Achou o ótimo | Erro médio | Pior erro "
             "| Épocas (média) | Tempo (média) |\n|---|---|---|---|---|---|---|---|")


def testar(n_pontos, tamanho_populacao, taxa_mutacao, tipo_mutacao, max_geracoes, max_estagnacao, seeds):
    pontos = ag.gerar_pontos_circulo(n_pontos, RAIO)
    otimo = ag.distancia_otima_circulo(n_pontos, RAIO)
    soma_erros = 0
    pior_erro = 0
    soma_epocas = 0
    soma_tempos = 0
    acertos = 0

    for seed in seeds:
        random.seed(seed)
        historico = ag.executar_algoritmo_genetico(
            pontos, tamanho_populacao, TAXA_SELECAO, taxa_mutacao,
            max_geracoes, max_estagnacao, mostrar_progresso=False, tipo_mutacao=tipo_mutacao)

        # O ótimo é o menor valor possível; max(0, ...) só evita "-0.00%" por arredondamento
        erro = max(0, (historico["melhores"][-1] - otimo) / otimo * 100)
        soma_erros += erro
        pior_erro = max(pior_erro, erro)
        soma_epocas += len(historico["melhores"]) - 1
        soma_tempos += historico["tempo_total"]
        if erro < 0.01:
            acertos += 1

    n = len(seeds)
    print(f"| {tipo_mutacao} | {taxa_mutacao:.0%} | {tamanho_populacao} | {acertos}/{n} | "
          f"{soma_erros / n:.2f}% | {pior_erro:.2f}% | {soma_epocas / n:.0f} | {soma_tempos / n:.2f} s |")


def testar_aleatorio(taxa_mutacao, tipo_mutacao):
    # Nos pontos aleatórios não há ótimo conhecido: comparamos a distância média
    # em 10 conjuntos de pontos diferentes (os mesmos para todas as configurações)
    soma_distancias = 0
    pior_distancia = 0
    for seed in SEEDS:
        random.seed(1000 + seed)
        pontos = ag.gerar_pontos_aleatorios(PONTOS)
        random.seed(seed)
        historico = ag.executar_algoritmo_genetico(
            pontos, POPULACAO_PADRAO, TAXA_SELECAO, taxa_mutacao,
            MAX_GERACOES, MAX_ESTAGNACAO, mostrar_progresso=False, tipo_mutacao=tipo_mutacao)
        soma_distancias += historico["melhores"][-1]
        pior_distancia = max(pior_distancia, historico["melhores"][-1])
    print(f"| {tipo_mutacao} | {taxa_mutacao:.0%} | {soma_distancias / len(SEEDS):.2f} | {pior_distancia:.2f} |")


def testar_20(tamanho_populacao, taxa_mutacao, tipo_mutacao):
    testar(PONTOS, tamanho_populacao, taxa_mutacao, tipo_mutacao, MAX_GERACOES, MAX_ESTAGNACAO, SEEDS)


def testar_100(taxa_mutacao, tipo_mutacao):
    testar(PONTOS_BONUS, POPULACAO_PADRAO, taxa_mutacao, tipo_mutacao,
           MAX_GERACOES_BONUS, MAX_ESTAGNACAO_BONUS, SEEDS_BONUS)


print(f"Círculo com {PONTOS} pontos, {len(SEEDS)} seeds por configuração")

print("\nTipo e taxa de mutação (população 100):\n")
print(CABECALHO)
for tipo in ["swap", "inversao"]:
    for taxa in TAXAS_MUTACAO:
        testar_20(POPULACAO_PADRAO, taxa, tipo)

print(f"\n{PONTOS} pontos aleatórios, {len(SEEDS)} conjuntos de pontos diferentes (população 100):\n")
print("| Mutação | Taxa | Distância média | Pior distância |\n|---|---|---|---|")
for tipo in ["swap", "inversao"]:
    for taxa in [0.05, 0.20]:
        testar_aleatorio(taxa, tipo)

print("\nTamanho da população (mutação inversão 5%):\n")
print(CABECALHO)
for tamanho in TAMANHOS_POPULACAO:
    testar_20(tamanho, MUTACAO_PADRAO, "inversao")

if "--bonus" in sys.argv:
    print(f"\nCírculo com {PONTOS_BONUS} pontos, {len(SEEDS_BONUS)} seeds por configuração (população 100):\n")
    print(CABECALHO)
    testar_100(MUTACAO_PADRAO, "swap")
    for taxa in TAXAS_MUTACAO_BONUS:
        testar_100(taxa, "inversao")
