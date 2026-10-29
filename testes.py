"""Testes simples do algoritmo genético. Rodar com: python testes.py"""
import math
import random
import time

import algoritmo_genetico as ag

N = 10


def eh_permutacao(rota, n):
    # Tem n cidades e cada cidade de 0 a n-1 aparece exatamente uma vez
    return sorted(rota) == list(range(n))


def testar_populacao_inicial():
    populacao = ag.criar_populacao(50, N)
    assert len(populacao) == 50
    for individuo in populacao:
        assert eh_permutacao(individuo, N)


def testar_distancia_fecha_o_ciclo():
    # Quadrado de lado 10: sem a volta seriam 30, com a volta são 40
    quadrado = [(0, 0), (10, 0), (10, 10), (0, 10)]
    assert math.isclose(ag.distancia_total([0, 1, 2, 3], quadrado), 40)


def testar_distancia_otima_do_circulo():
    # Visitar o círculo em ordem deve dar exatamente o ótimo teórico
    pontos = ag.gerar_pontos_circulo(N, 40)
    rota_em_ordem = list(range(N))
    assert math.isclose(ag.distancia_total(rota_em_ordem, pontos), ag.distancia_otima_circulo(N, 40))


def testar_minimo_de_pontos():
    assert len(ag.gerar_pontos_aleatorios(8)) == 8
    assert len(ag.gerar_pontos_circulo(8, 40)) == 8
    try:
        ag.gerar_pontos_aleatorios(7)
        assert False, "deveria recusar menos de 8 pontos"
    except ValueError:
        pass

    try:
        ag.gerar_pontos_circulo(7, 40)
        assert False, "deveria recusar menos de 8 pontos"
    except ValueError:
        pass


def testar_ordem_da_populacao():
    pontos = ag.gerar_pontos_aleatorios(N)
    populacao, distancias = ag.ordenar_populacao(ag.criar_populacao(30, N), pontos)
    assert distancias == sorted(distancias)
    assert math.isclose(distancias[0], ag.distancia_total(populacao[0], pontos))


def testar_crossover_exemplo_da_aula():
    # Pais A E C B F D e A D C E B F, trecho das 3 primeiras posições -> A E C D B F
    A, B, C, D, E, F = range(6)
    filho = ag.ordered_crossover([A, E, C, B, F, D], [A, D, C, E, B, F], 0, 3)
    assert filho == [A, E, C, D, B, F]


def testar_crossover_trecho_no_meio():
    pai1 = [0, 1, 2, 3, 4, 5, 6, 7]
    pai2 = [4, 6, 1, 0, 7, 3, 5, 2]
    # O trecho [2, 3, 4] fica nas posições 2 a 4; o resto entra na ordem do pai2: 6 1 0 7 5
    assert ag.ordered_crossover(pai1, pai2, 2, 5) == [6, 1, 2, 3, 4, 0, 7, 5]
    # Pais iguais geram um filho igual
    assert ag.ordered_crossover(pai1, pai1, 2, 5) == pai1


def testar_crossover_sem_repetir_cidades():
    for i in range(1000):
        pai1 = random.sample(range(N), N)
        pai2 = random.sample(range(N), N)
        inicio, fim = sorted(random.sample(range(N + 1), 2))
        filho = ag.ordered_crossover(pai1, pai2, inicio, fim)
        assert eh_permutacao(filho, N)
        assert filho[inicio:fim] == pai1[inicio:fim]


def testar_mutacao_swap():
    for i in range(1000):
        individuo = random.sample(range(N), N)
        original = individuo[:]
        ag.mutacao_swap(individuo)
        assert eh_permutacao(individuo, N)

        posicoes_diferentes = 0
        for posicao in range(N):
            if individuo[posicao] != original[posicao]:
                posicoes_diferentes += 1
        assert posicoes_diferentes == 2


def testar_mutacao_inversao():
    # O trecho entre as posições sorteadas fica invertido e o resto não muda
    random.seed(3)
    individuo = [0, 1, 2, 3, 4, 5, 6, 7]
    ag.mutacao_inversao(individuo)
    random.seed(3)
    i, j = sorted(random.sample(range(8), 2))
    esperado = [0, 1, 2, 3, 4, 5, 6, 7]
    esperado[i:j + 1] = esperado[i:j + 1][::-1]
    assert individuo == esperado
    assert individuo != [0, 1, 2, 3, 4, 5, 6, 7]

    for k in range(1000):
        individuo = random.sample(range(N), N)
        ag.mutacao_inversao(individuo)
        assert eh_permutacao(individuo, N)


def testar_inversao_desfaz_cruzamento():
    # Quadrado visitado em "X" (0 -> 2 -> 1 -> 3) tem as diagonais se cruzando.
    # Inverter o trecho [2, 1] desfaz o cruzamento e chega ao perímetro (40).
    quadrado = [(0, 0), (10, 0), (10, 10), (0, 10)]
    rota_cruzada = [0, 2, 1, 3]
    rota_cruzada[1:3] = rota_cruzada[1:3][::-1]
    assert rota_cruzada == [0, 1, 2, 3]
    assert math.isclose(ag.distancia_total(rota_cruzada, quadrado), 40)


def testar_nova_geracao():
    pontos = ag.gerar_pontos_aleatorios(N)
    populacao = ag.criar_populacao(30, N)
    for i in range(20):
        populacao, distancias = ag.ordenar_populacao(populacao, pontos)
        melhor = populacao[0]
        populacao = ag.nova_geracao(populacao, 0.5, 0.05)
        assert len(populacao) == 30
        assert populacao[0] == melhor  # elitismo
        for individuo in populacao:
            assert eh_permutacao(individuo, N)

    # O mesmo com a mutação swap
    populacao, distancias = ag.ordenar_populacao(populacao, pontos)
    populacao = ag.nova_geracao(populacao, 0.5, 1.0, "swap")
    for individuo in populacao:
        assert eh_permutacao(individuo, N)


def testar_tempo_nao_conta_desenho():
    # Uma "janela" lenta não pode aumentar o tempo medido do algoritmo
    def janela_lenta(pontos, epoca, rota, distancia):
        time.sleep(0.01)

    pontos = ag.gerar_pontos_aleatorios(N)
    historico = ag.executar_algoritmo_genetico(pontos, 20, 0.5, 0.05, 30, 1000, janela_lenta, 1,
                                               mostrar_progresso=False)
    # 31 desenhos de 0,01 s somariam mais de 0,3 s
    assert historico["tempo_total"] < 0.3
    assert historico["tempo_ultima_melhoria"] <= historico["tempo_total"]


def testar_algoritmo_completo():
    pontos = ag.gerar_pontos_circulo(N, 40)
    historico = ag.executar_algoritmo_genetico(pontos, 50, 0.5, 0.05, 100, 30, mostrar_progresso=False)

    # Termina por limite de épocas ou por estagnação
    epocas = len(historico["melhores"]) - 1
    assert epocas == 100 or epocas >= 30

    # Com elitismo a melhor distância nunca piora
    melhores = historico["melhores"]
    for i in range(1, len(melhores)):
        assert melhores[i] <= melhores[i - 1]

    # Todas as rotas são válidas e a distância registrada confere
    for i in range(len(historico["rotas"])):
        assert eh_permutacao(historico["rotas"][i], N)
        assert math.isclose(ag.distancia_total(historico["rotas"][i], pontos), melhores[i])


def testar_parada_por_estagnacao():
    pontos = ag.gerar_pontos_aleatorios(N)
    historico = ag.executar_algoritmo_genetico(pontos, 20, 0.5, 0.05, 100000, 15, mostrar_progresso=False)
    epocas = len(historico["melhores"]) - 1
    assert epocas == historico["epoca_ultima_melhoria"] + 15


def testar_mesma_seed_mesmo_resultado():
    resultados = []
    for i in range(2):
        random.seed(7)
        pontos = ag.gerar_pontos_aleatorios(N)
        historico = ag.executar_algoritmo_genetico(pontos, 30, 0.5, 0.05, 50, 20, mostrar_progresso=False)
        resultados.append(historico["rotas"][-1])
    assert resultados[0] == resultados[1]


testes = [
    testar_populacao_inicial,
    testar_distancia_fecha_o_ciclo,
    testar_distancia_otima_do_circulo,
    testar_minimo_de_pontos,
    testar_ordem_da_populacao,
    testar_crossover_exemplo_da_aula,
    testar_crossover_trecho_no_meio,
    testar_crossover_sem_repetir_cidades,
    testar_mutacao_swap,
    testar_mutacao_inversao,
    testar_inversao_desfaz_cruzamento,
    testar_nova_geracao,
    testar_tempo_nao_conta_desenho,
    testar_algoritmo_completo,
    testar_parada_por_estagnacao,
    testar_mesma_seed_mesmo_resultado,
]

random.seed(0)
for teste in testes:
    teste()
    print("OK", teste.__name__)
print("Todos os testes passaram.")
