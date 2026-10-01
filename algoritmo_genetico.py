import math
import random
import time

MIN_PONTOS = 8
TOLERANCIA_MELHORA = 1e-9


# ---------------------------------------------------------------------------
# Pontos e distância
# ---------------------------------------------------------------------------

def validar_quantidade_pontos(n):
    if n < MIN_PONTOS:
        raise ValueError(f"O problema precisa de pelo menos {MIN_PONTOS} pontos (recebeu {n}).")


def gerar_pontos_aleatorios(n, limite=100):
    validar_quantidade_pontos(n)
    return [(random.uniform(0, limite), random.uniform(0, limite)) for _ in range(n)]


def gerar_pontos_circulo(n, raio, centro_x=50, centro_y=50):
    validar_quantidade_pontos(n)
    pontos = []
    for i in range(n):
        angulo = 2 * math.pi * i / n
        pontos.append((centro_x + raio * math.cos(angulo), centro_y + raio * math.sin(angulo)))
    return pontos


def distancia_otima_circulo(n, raio):
    # Percorrer o círculo em ordem: n lados iguais de um polígono regular
    lado = 2 * raio * math.sin(math.pi / n)
    return n * lado


def distancia(a, b):
    return math.sqrt((b[0] - a[0]) ** 2 + (b[1] - a[1]) ** 2)


# ---------------------------------------------------------------------------
# Indivíduo (genótipo) e população
# ---------------------------------------------------------------------------

def criar_individuo(n):
    # Permutação das cidades 0..n-1: a ordem em que elas são visitadas
    individuo = list(range(n))
    random.shuffle(individuo)
    return individuo


def criar_populacao(tamanho_populacao, n):
    return [criar_individuo(n) for _ in range(tamanho_populacao)]


def eh_permutacao_valida(individuo, n):
    # Exatamente n genes e cada cidade aparecendo uma única vez
    return len(individuo) == n and sorted(individuo) == list(range(n))


# ---------------------------------------------------------------------------
# Função de aptidão (custo a ser MINIMIZADO)
# ---------------------------------------------------------------------------

def distancia_total(individuo, pontos):
    total = 0
    for i in range(len(individuo) - 1):
        total += distancia(pontos[individuo[i]], pontos[individuo[i + 1]])
    # Fechamento do ciclo: volta da última cidade para a primeira
    total += distancia(pontos[individuo[-1]], pontos[individuo[0]])
    return total


def ranking(populacao, pontos):
    """Ordena a população da menor distância (melhor) para a maior (pior)."""
    avaliados = [(distancia_total(individuo, pontos), individuo) for individuo in populacao]
    avaliados.sort(key=lambda par: par[0])
    populacao_ordenada = [individuo for _, individuo in avaliados]
    distancias = [d for d, _ in avaliados]
    return populacao_ordenada, distancias


# ---------------------------------------------------------------------------
# Seleção, cruzamento e mutação
# ---------------------------------------------------------------------------

def selecionar_pais(populacao_ordenada, taxa_selecao):
    # Top Ranking: só os melhores (população já ordenada) podem se reproduzir
    quantidade = max(2, int(len(populacao_ordenada) * taxa_selecao))
    return populacao_ordenada[:quantidade]


def montar_filho(pai1, pai2, inicio, fim):
    trecho = pai1[inicio:fim]
    ja_no_filho = set(trecho)
    resto = [cidade for cidade in pai2 if cidade not in ja_no_filho]
    # O trecho fica na mesma posição do pai1; as posições livres recebem o resto na ordem do pai2
    return resto[:inicio] + trecho + resto[inicio:]


def ordered_crossover(pai1, pai2):
    # Dois pontos de corte distintos; o trecho pai1[inicio:fim] nunca fica vazio
    inicio, fim = sorted(random.sample(range(len(pai1) + 1), 2))
    return montar_filho(pai1, pai2, inicio, fim)


def mutacao_swap(individuo):
    i, j = random.sample(range(len(individuo)), 2)
    individuo[i], individuo[j] = individuo[j], individuo[i]


def nova_geracao(populacao_ordenada, tamanho_populacao, taxa_selecao, taxa_mutacao):
    pais = selecionar_pais(populacao_ordenada, taxa_selecao)

    # Elitismo: o melhor indivíduo sobrevive para a próxima geração
    nova_populacao = [populacao_ordenada[0]]

    while len(nova_populacao) < tamanho_populacao:
        pai1, pai2 = random.sample(pais, 2)
        filho = ordered_crossover(pai1, pai2)
        if random.random() < taxa_mutacao:
            mutacao_swap(filho)
        nova_populacao.append(filho)

    return nova_populacao


# ---------------------------------------------------------------------------
# Loop das épocas
# ---------------------------------------------------------------------------

def executar_algoritmo_genetico(pontos, tamanho_populacao, taxa_selecao, taxa_mutacao,
                                max_geracoes, max_estagnacao,
                                atualizar_tela=None, intervalo_tela=10, mostrar_progresso=True):
    """
    Executa o AG e devolve o histórico de todas as épocas.

    A época 0 é a população inicial aleatória; cada época seguinte é uma nova
    geração. `atualizar_tela(epoca, individuo, distancia)` é opcional e serve
    para desenhar a melhor rota durante a execução.
    """
    n = len(pontos)
    validar_quantidade_pontos(n)

    historico = {
        "epocas": [],
        "melhor_da_epoca": [],
        "melhor_ate_agora": [],
        "media": [],
        "melhor_individuo": [],
    }

    populacao = criar_populacao(tamanho_populacao, n)
    melhor_individuo = None
    melhor_distancia = math.inf
    epoca_ultima_melhoria = 0
    tempo_ultima_melhoria = 0
    epocas_sem_melhora = 0
    epoca = 0
    inicio = time.perf_counter()

    while True:
        # 1. Ranking dos indivíduos pela aptidão
        populacao, distancias = ranking(populacao, pontos)

        if distancias[0] < melhor_distancia - TOLERANCIA_MELHORA:
            melhor_distancia = distancias[0]
            melhor_individuo = populacao[0][:]
            epoca_ultima_melhoria = epoca
            tempo_ultima_melhoria = time.perf_counter() - inicio
            epocas_sem_melhora = 0
        else:
            epocas_sem_melhora += 1

        media = sum(distancias) / len(distancias)
        historico["epocas"].append(epoca)
        historico["melhor_da_epoca"].append(distancias[0])
        historico["melhor_ate_agora"].append(melhor_distancia)
        historico["media"].append(media)
        historico["melhor_individuo"].append(melhor_individuo)

        if mostrar_progresso:
            print(f"Epoca {epoca} | Melhor: {melhor_distancia:.2f} | Media: {media:.2f}")

        # 2. Critérios de parada: limite de épocas ou estagnação
        parar = epoca >= max_geracoes or epocas_sem_melhora >= max_estagnacao

        if atualizar_tela and (epoca % intervalo_tela == 0 or parar):
            atualizar_tela(epoca, melhor_individuo, melhor_distancia)

        if parar:
            break

        # 3 e 4. Seleção + criação da nova geração (cruzamento e mutação)
        populacao = nova_geracao(populacao, tamanho_populacao, taxa_selecao, taxa_mutacao)
        epoca += 1

    if not eh_permutacao_valida(melhor_individuo, n):
        raise RuntimeError("A melhor rota encontrada não é uma permutação válida.")

    historico["melhor_distancia"] = melhor_distancia
    historico["melhor_rota"] = melhor_individuo
    historico["total_epocas"] = epoca
    historico["epoca_ultima_melhoria"] = epoca_ultima_melhoria
    historico["tempo_total"] = time.perf_counter() - inicio
    historico["tempo_ultima_melhoria"] = tempo_ultima_melhoria
    return historico
