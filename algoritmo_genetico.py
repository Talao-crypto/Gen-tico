import math
import random
import time

MIN_PONTOS = 8


# ---------------------------------------------------------------------------
# Pontos (cidades)
# ---------------------------------------------------------------------------

def gerar_pontos_aleatorios(n, limite=100):
    if n < MIN_PONTOS:
        raise ValueError("São necessários pelo menos 8 pontos.")
    pontos = []
    for i in range(n):
        x = random.uniform(0, limite)
        y = random.uniform(0, limite)
        pontos.append((x, y))
    return pontos


def gerar_pontos_circulo(n, raio, centro_x=50, centro_y=50):
    if n < MIN_PONTOS:
        raise ValueError("São necessários pelo menos 8 pontos.")
    pontos = []
    for i in range(n):
        angulo = 2 * math.pi * i / n
        x = centro_x + raio * math.cos(angulo)
        y = centro_y + raio * math.sin(angulo)
        pontos.append((x, y))
    return pontos


def distancia_otima_circulo(n, raio):
    # O melhor caminho percorre o círculo em ordem: um polígono regular de n lados
    lado = 2 * raio * math.sin(math.pi / n)
    return n * lado


# ---------------------------------------------------------------------------
# Indivíduo = lista com a ordem de visita das cidades (uma permutação de 0..n-1)
# ---------------------------------------------------------------------------

def criar_populacao(tamanho_populacao, n):
    populacao = []
    for i in range(tamanho_populacao):
        individuo = list(range(n))
        random.shuffle(individuo)
        populacao.append(individuo)
    return populacao


def distancia_total(individuo, pontos):
    n = len(individuo)
    total = 0
    for i in range(n):
        x1, y1 = pontos[individuo[i]]
        # A última cidade volta para a primeira (i + 1 == n vira 0)
        x2, y2 = pontos[individuo[(i + 1) % n]]
        total += math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
    return total


def pegar_distancia(par):
    return par[0]


def ordenar_populacao(populacao, pontos):
    """Devolve a população ordenada do melhor (menor distância) ao pior, e as distâncias."""
    pares = []
    for individuo in populacao:
        pares.append((distancia_total(individuo, pontos), individuo))
    pares.sort(key=pegar_distancia)

    populacao_ordenada = []
    distancias = []
    for distancia, individuo in pares:
        populacao_ordenada.append(individuo)
        distancias.append(distancia)
    return populacao_ordenada, distancias


# ---------------------------------------------------------------------------
# Cruzamento e mutação
# ---------------------------------------------------------------------------

def ordered_crossover(pai1, pai2, inicio, fim):
    # O trecho de pai1 vai para o filho na mesma posição em que estava
    trecho = pai1[inicio:fim]

    # O resto das cidades vem do pai2, na ordem do pai2, sem repetir as do trecho
    resto = []
    for cidade in pai2:
        if cidade not in trecho:
            resto.append(cidade)

    # As cidades do resto ocupam as posições livres, antes e depois do trecho
    return resto[:inicio] + trecho + resto[inicio:]


def mutacao_swap(individuo):
    i, j = random.sample(range(len(individuo)), 2)
    individuo[i], individuo[j] = individuo[j], individuo[i]


def nova_geracao(populacao_ordenada, taxa_selecao, taxa_mutacao):
    tamanho_populacao = len(populacao_ordenada)
    n = len(populacao_ordenada[0])

    # Seleção Top Ranking: só os melhores (a lista já está ordenada) podem ser pais
    quantidade_pais = max(2, int(tamanho_populacao * taxa_selecao))
    pais = populacao_ordenada[:quantidade_pais]

    # Elitismo: o melhor indivíduo passa direto para a próxima geração
    nova_populacao = [populacao_ordenada[0]]

    while len(nova_populacao) < tamanho_populacao:
        pai1, pai2 = random.sample(pais, 2)
        inicio, fim = sorted(random.sample(range(n + 1), 2))
        filho = ordered_crossover(pai1, pai2, inicio, fim)
        if random.random() < taxa_mutacao:
            mutacao_swap(filho)
        nova_populacao.append(filho)

    return nova_populacao


# ---------------------------------------------------------------------------
# Algoritmo genético completo
# ---------------------------------------------------------------------------

def executar_algoritmo_genetico(pontos, tamanho_populacao, taxa_selecao, taxa_mutacao,
                                max_geracoes, max_estagnacao,
                                ao_vivo=None, intervalo_ao_vivo=10, mostrar_progresso=True):
    """
    Roda o algoritmo e devolve um dicionário com o histórico.

    A época 0 é a população inicial aleatória. Nas listas do histórico,
    a posição i guarda o valor da época i.
    ao_vivo(pontos, epoca, rota, distancia) é opcional: desenha a rota durante a execução.
    """
    historico = {
        "melhores": [],   # menor distância de cada época
        "medias": [],     # distância média da população em cada época
        "rotas": [],      # melhor rota de cada época
    }

    populacao = criar_populacao(tamanho_populacao, len(pontos))
    melhor_distancia = math.inf
    epoca_ultima_melhoria = 0
    tempo_ultima_melhoria = 0
    epocas_sem_melhora = 0
    epoca = 0
    inicio_tempo = time.perf_counter()

    while True:
        populacao, distancias = ordenar_populacao(populacao, pontos)
        melhor_rota = populacao[0]

        # Só conta como melhora se for maior que 1e-9 (evita erros de arredondamento)
        if distancias[0] < melhor_distancia - 1e-9:
            epoca_ultima_melhoria = epoca
            tempo_ultima_melhoria = time.perf_counter() - inicio_tempo
            epocas_sem_melhora = 0
        else:
            epocas_sem_melhora += 1
        melhor_distancia = distancias[0]

        media = sum(distancias) / len(distancias)
        historico["melhores"].append(melhor_distancia)
        historico["medias"].append(media)
        historico["rotas"].append(melhor_rota[:])

        if mostrar_progresso:
            print(f"Época {epoca} | Melhor: {melhor_distancia:.2f} | Média: {media:.2f}")

        # Parada: limite de épocas ou estagnação (muitas épocas sem melhorar)
        parar = epoca >= max_geracoes or epocas_sem_melhora >= max_estagnacao

        if ao_vivo is not None and (epoca % intervalo_ao_vivo == 0 or parar):
            ao_vivo(pontos, epoca, melhor_rota, melhor_distancia)

        if parar:
            break

        populacao = nova_geracao(populacao, taxa_selecao, taxa_mutacao)
        epoca += 1

    historico["epoca_ultima_melhoria"] = epoca_ultima_melhoria
    historico["tempo_ultima_melhoria"] = tempo_ultima_melhoria
    historico["tempo_total"] = time.perf_counter() - inicio_tempo
    return historico
