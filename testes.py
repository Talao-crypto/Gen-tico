"""Verificações simples do algoritmo genético. Rodar com: python testes.py"""
import math
import random

import algoritmo_genetico as ag

N = 10
REPETICOES = 1000


def testar_populacao_inicial():
    populacao = ag.criar_populacao(50, N)
    for individuo in populacao:
        assert len(individuo) == N, "indivíduo com quantidade errada de genes"
        assert ag.eh_permutacao_valida(individuo, N), "cidade repetida ou ausente"


def testar_crossover_exemplo_da_aula():
    # Slide "Ordered Crossover": A=[A,E,C,B,F,D], B=[A,D,C,E,B,F] -> [A,E,C,D,B,F]
    A, B, C, D, E, F = range(6)
    pai1 = [A, E, C, B, F, D]
    pai2 = [A, D, C, E, B, F]
    assert ag.montar_filho(pai1, pai2, 0, 3) == [A, E, C, D, B, F]


def testar_crossover_trecho_no_meio():
    pai1 = [0, 1, 2, 3, 4, 5, 6, 7]
    pai2 = [4, 6, 1, 0, 7, 3, 5, 2]
    # Trecho [2, 3, 4] fica nas posições 2..4; o resto entra na ordem do pai2: 6 1 0 7 5
    assert ag.montar_filho(pai1, pai2, 2, 5) == [6, 1, 2, 3, 4, 0, 7, 5]
    # Pais iguais devem gerar um filho igual (o cruzamento não destrói a rota)
    assert ag.montar_filho(pai1, pai1, 2, 5) == pai1


def testar_crossover_sem_repeticao():
    for _ in range(REPETICOES):
        pai1, pai2 = ag.criar_individuo(N), ag.criar_individuo(N)
        filho = ag.ordered_crossover(pai1, pai2)
        assert ag.eh_permutacao_valida(filho, N), f"crossover inválido: {filho}"


def testar_mutacao_mantem_permutacao():
    for _ in range(REPETICOES):
        individuo = ag.criar_individuo(N)
        original = individuo[:]
        ag.mutacao_swap(individuo)
        assert ag.eh_permutacao_valida(individuo, N), f"mutação inválida: {individuo}"
        diferentes = sum(1 for a, b in zip(original, individuo) if a != b)
        assert diferentes == 2, "swap deve trocar exatamente duas posições"


def testar_distancia_fecha_ciclo():
    # Quadrado de lado 10: sem a volta seriam 30, com a volta são 40
    quadrado = [(0, 0), (10, 0), (10, 10), (0, 10)]
    assert math.isclose(ag.distancia_total([0, 1, 2, 3], quadrado), 40)

    # No círculo, visitar os pontos em ordem deve dar exatamente o ótimo teórico
    pontos = ag.gerar_pontos_circulo(N, 40)
    assert math.isclose(ag.distancia_total(list(range(N)), pontos), ag.distancia_otima_circulo(N, 40))


def testar_minimo_de_pontos():
    assert len(ag.gerar_pontos_aleatorios(8)) == 8
    assert len(ag.gerar_pontos_circulo(8, 40)) == 8
    try:
        ag.gerar_pontos_aleatorios(7)
    except ValueError:
        pass
    else:
        raise AssertionError("deveria recusar menos de 8 pontos")


def testar_tamanho_populacao_constante():
    pontos = ag.gerar_pontos_aleatorios(N)
    populacao = ag.criar_populacao(30, N)
    for _ in range(20):
        populacao, _ = ag.ranking(populacao, pontos)
        populacao = ag.nova_geracao(populacao, 30, 0.5, 0.05)
        assert len(populacao) == 30, "tamanho da população mudou"
        assert all(ag.eh_permutacao_valida(individuo, N) for individuo in populacao)


if __name__ == "__main__":
    random.seed(0)
    testes = [
        testar_populacao_inicial,
        testar_crossover_exemplo_da_aula,
        testar_crossover_trecho_no_meio,
        testar_crossover_sem_repeticao,
        testar_mutacao_mantem_permutacao,
        testar_distancia_fecha_ciclo,
        testar_minimo_de_pontos,
        testar_tamanho_populacao_constante,
    ]
    for teste in testes:
        teste()
        print(f"OK  {teste.__name__}")
    print("Todos os testes passaram.")
