import csv
import os
import random
import sys

import algoritmo_genetico as ag
import visualizacao as vis

# ---------------------------------------------------------------------------
# Parâmetros
# ---------------------------------------------------------------------------

SEED = 42

TAMANHO_POPULACAO = 100
TAXA_SELECAO = 0.5       # Top Ranking: os 50% melhores podem ser pais
TAXA_MUTACAO = 0.05
MAX_GERACOES = 500
MAX_ESTAGNACAO = 100     # para se a melhor distância não melhorar por 100 épocas

PONTOS_ALEATORIO = 20
PONTOS_CIRCULO = 20
RAIO = 40

# O bônus tem mais pontos, então precisa de mais épocas
PONTOS_BONUS = 100
MAX_GERACOES_BONUS = 20000
MAX_ESTAGNACAO_BONUS = 2000

ATUALIZAR_A_CADA = 10    # a janela ao vivo é redesenhada a cada 10 épocas
MOSTRAR_JANELA = "--sem-janela" not in sys.argv

PASTA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "resultados")


# ---------------------------------------------------------------------------
# Um cenário completo: roda o algoritmo, mostra o resultado e salva os arquivos
# ---------------------------------------------------------------------------

def executar_cenario(nome, arquivo, pontos, distancia_otima, max_geracoes, max_estagnacao,
                     epocas_para_salvar):
    print(f"\n===== {nome}: {len(pontos)} pontos =====")

    ao_vivo = None
    if MOSTRAR_JANELA:
        vis.abrir_janela(nome)
        ao_vivo = vis.atualizar_janela

    historico = ag.executar_algoritmo_genetico(
        pontos, TAMANHO_POPULACAO, TAXA_SELECAO, TAXA_MUTACAO,
        max_geracoes, max_estagnacao, ao_vivo, ATUALIZAR_A_CADA)

    ultima_epoca = len(historico["melhores"]) - 1
    melhor_distancia = historico["melhores"][ultima_epoca]

    print(f"\n--- Resultado: {nome} ---")
    print(f"Melhor rota: {historico['rotas'][ultima_epoca]}")
    print(f"Distância da melhor rota: {melhor_distancia:.2f}")
    print(f"Épocas executadas: {ultima_epoca}")
    print(f"Época da última melhoria: {historico['epoca_ultima_melhoria']}")
    print(f"Tempo total: {historico['tempo_total']:.2f} s")
    print(f"Tempo até a última melhoria: {historico['tempo_ultima_melhoria']:.2f} s")

    if distancia_otima is not None:
        diferenca = melhor_distancia - distancia_otima
        print(f"Distância ótima teórica: {distancia_otima:.2f}")
        print(f"Diferença absoluta: {diferenca:.2f}")
        print(f"Erro percentual: {diferenca / distancia_otima * 100:.2f}%")

    # Imagens da rota nas épocas pedidas e na última
    for epoca in epocas_para_salvar + [ultima_epoca]:
        if epoca <= ultima_epoca:
            distancia = historico["melhores"][epoca]
            titulo = f"{nome} | Época {epoca} | Distância: {distancia:.2f}"
            caminho = os.path.join(PASTA, f"{arquivo}_epoca_{epoca}.png")
            vis.salvar_rota(pontos, historico["rotas"][epoca], titulo, caminho)

    vis.salvar_convergencia(historico, f"Convergência - {nome}",
                            os.path.join(PASTA, f"{arquivo}_convergencia.png"), distancia_otima)

    # Histórico de todas as épocas em CSV
    with open(os.path.join(PASTA, f"{arquivo}_historico.csv"), "w", newline="") as arq:
        escritor = csv.writer(arq)
        escritor.writerow(["epoca", "melhor", "media", "melhor_rota"])
        for epoca in range(ultima_epoca + 1):
            rota = " ".join(str(cidade) for cidade in historico["rotas"][epoca])
            escritor.writerow([epoca, round(historico["melhores"][epoca], 4),
                               round(historico["medias"][epoca], 4), rota])


# ---------------------------------------------------------------------------
# Os três experimentos (cada um recomeça da mesma seed)
# ---------------------------------------------------------------------------

os.makedirs(PASTA, exist_ok=True)

random.seed(SEED)
pontos = ag.gerar_pontos_aleatorios(PONTOS_ALEATORIO)
executar_cenario("Aleatório", "aleatorio", pontos, None, MAX_GERACOES, MAX_ESTAGNACAO, [0])

random.seed(SEED)
pontos = ag.gerar_pontos_circulo(PONTOS_CIRCULO, RAIO)
otimo = ag.distancia_otima_circulo(PONTOS_CIRCULO, RAIO)
executar_cenario("Círculo", "circular", pontos, otimo, MAX_GERACOES, MAX_ESTAGNACAO, [0])

random.seed(SEED)
pontos = ag.gerar_pontos_circulo(PONTOS_BONUS, RAIO)
otimo = ag.distancia_otima_circulo(PONTOS_BONUS, RAIO)
executar_cenario("Bônus", "bonus", pontos, otimo, MAX_GERACOES_BONUS, MAX_ESTAGNACAO_BONUS,
                 [0, 10, 50, 100])

if MOSTRAR_JANELA:
    vis.mostrar_janelas()
