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
TIPO_MUTACAO = "inversao"  # "inversao" (usada) ou "swap" (para comparar)
MAX_GERACOES = 500
MAX_ESTAGNACAO = 100     # para se a melhor distância não melhorar por 100 épocas

PONTOS_ALEATORIO = 20
PONTOS_CIRCULO = 20
RAIO = 40

# O bônus tem mais pontos, então precisa de mais épocas
PONTOS_BONUS = 100
MAX_GERACOES_BONUS = 20000
MAX_ESTAGNACAO_BONUS = 2000

# Nos cenários de 20 pontos a janela ao vivo mostra todas as épocas.
# No bônus são milhares de épocas, então a janela e o GIF mostram uma a cada 100.
ATUALIZAR_A_CADA = 1
ATUALIZAR_A_CADA_BONUS = 100

# Épocas que viram imagem (.png) em resultados/; a última época sempre vira imagem.
# Nos cenários de 20 pontos só a última, porque a janela ao vivo já mostra todas.
EPOCAS_IMAGENS = []
EPOCAS_IMAGENS_BONUS = [0, 10, 50, 100, 500, 1000, 2000, 3000, 5000]

MOSTRAR_JANELA = "--sem-janela" not in sys.argv

PASTA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "resultados")


# ---------------------------------------------------------------------------
# Um cenário completo: roda o algoritmo, mostra o resultado e salva os arquivos
# ---------------------------------------------------------------------------

def executar_cenario(nome, arquivo, pontos, distancia_otima, max_geracoes, max_estagnacao,
                     atualizar_a_cada, epocas_imagens, mostrar_rota, salvar_gif):
    print(f"\n===== {nome}: {len(pontos)} pontos =====")

    ao_vivo = None
    if MOSTRAR_JANELA:
        ao_vivo = vis.atualizar_janela

    historico = ag.executar_algoritmo_genetico(
        pontos, TAMANHO_POPULACAO, TAXA_SELECAO, TAXA_MUTACAO,
        max_geracoes, max_estagnacao, ao_vivo, atualizar_a_cada,
        mostrar_rota=mostrar_rota, tipo_mutacao=TIPO_MUTACAO)

    ultima_epoca = len(historico["melhores"]) - 1
    melhor_distancia = historico["melhores"][ultima_epoca]

    # Resumo do resultado na tela
    resumo = [
        f"Cenário: {nome} ({len(pontos)} pontos)",
        f"Parâmetros: população {TAMANHO_POPULACAO}, seleção {TAXA_SELECAO:.0%}, "
        f"mutação {TIPO_MUTACAO} {TAXA_MUTACAO:.0%}, "
        f"máximo {max_geracoes} épocas, estagnação {max_estagnacao} épocas, seed {SEED}",
        f"Melhor rota: {historico['rotas'][ultima_epoca]}",
        f"Distância da melhor rota: {melhor_distancia:.2f}",
        f"Épocas executadas: {ultima_epoca}",
        f"Época da última melhoria: {historico['epoca_ultima_melhoria']}",
        f"Tempo total: {historico['tempo_total']:.2f} s",
        f"Tempo até a última melhoria (convergência): {historico['tempo_ultima_melhoria']:.2f} s",
    ]
    if distancia_otima is not None:
        diferenca = melhor_distancia - distancia_otima
        if abs(diferenca) < 1e-6:
            diferenca = 0  # evita mostrar "-0.00" por arredondamento
        resumo.append(f"Distância ótima teórica: {distancia_otima:.2f}")
        resumo.append(f"Diferença absoluta: {diferenca:.2f}")
        resumo.append(f"Erro percentual: {diferenca / distancia_otima * 100:.2f}%")

    print(f"\n--- Resultado: {nome} ---")
    for linha in resumo:
        print(linha)

    # Imagens da rota em algumas épocas e na última
    for epoca in epocas_imagens + [ultima_epoca]:
        if epoca <= ultima_epoca:
            distancia = historico["melhores"][epoca]
            titulo = f"{nome} | Época {epoca} | Distância: {distancia:.2f}"
            caminho = os.path.join(PASTA, f"{arquivo}_epoca_{epoca}.png")
            vis.salvar_rota(pontos, historico["rotas"][epoca], titulo, caminho)

    # Animação com a melhor rota a cada `atualizar_a_cada` épocas
    if salvar_gif:
        vis.salvar_animacao(pontos, historico, nome,
                            os.path.join(PASTA, f"{arquivo}_evolucao.gif"), atualizar_a_cada)

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
executar_cenario("Aleatório", "aleatorio", pontos, None, MAX_GERACOES, MAX_ESTAGNACAO,
                 ATUALIZAR_A_CADA, EPOCAS_IMAGENS, True, False)

random.seed(SEED)
pontos = ag.gerar_pontos_circulo(PONTOS_CIRCULO, RAIO)
otimo = ag.distancia_otima_circulo(PONTOS_CIRCULO, RAIO)
executar_cenario("Círculo", "circular", pontos, otimo, MAX_GERACOES, MAX_ESTAGNACAO,
                 ATUALIZAR_A_CADA, EPOCAS_IMAGENS, True, False)

# No bônus a rota tem 100 cidades, então o console mostra só as distâncias
random.seed(SEED)
pontos = ag.gerar_pontos_circulo(PONTOS_BONUS, RAIO)
otimo = ag.distancia_otima_circulo(PONTOS_BONUS, RAIO)
executar_cenario("Bônus", "bonus", pontos, otimo, MAX_GERACOES_BONUS, MAX_ESTAGNACAO_BONUS,
                 ATUALIZAR_A_CADA_BONUS, EPOCAS_IMAGENS_BONUS, False, True)

if MOSTRAR_JANELA:
    vis.mostrar_janelas()
