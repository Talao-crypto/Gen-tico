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

POPULATION_SIZE = 100
SELECTION_RATE = 0.5      # Top Ranking: os 50% melhores podem ser pais
MUTATION_RATE = 0.05
MAX_GENERATIONS = 500
MAX_STAGNATION = 100

N_POINTS_RANDOM = 20
N_POINTS_CIRCLE = 20
CIRCLE_RADIUS = 40

# Bônus: círculo com muitos pontos precisa de mais épocas para convergir
N_POINTS_BONUS = 100
MAX_GENERATIONS_BONUS = 20000
MAX_STAGNATION_BONUS = 2000
BONUS_SNAPSHOT_EPOCHS = [0, 10, 50, 100]

VISUAL_UPDATE_INTERVAL = 10
MOSTRAR_JANELA = "--sem-janela" not in sys.argv

PASTA_RESULTADOS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "resultados")


# ---------------------------------------------------------------------------
# Funções auxiliares dos experimentos
# ---------------------------------------------------------------------------

def caminho_resultado(nome_arquivo):
    return os.path.join(PASTA_RESULTADOS, nome_arquivo)


def resolver(nome_cenario, pontos, max_geracoes, max_estagnacao):
    print(f"\n===== {nome_cenario}: {len(pontos)} pontos =====")
    atualizar_tela = vis.criar_janela_ao_vivo(pontos, nome_cenario) if MOSTRAR_JANELA else None
    historico = ag.executar_algoritmo_genetico(
        pontos, POPULATION_SIZE, SELECTION_RATE, MUTATION_RATE,
        max_geracoes, max_estagnacao, atualizar_tela, VISUAL_UPDATE_INTERVAL,
    )

    print(f"\n--- Resultado: {nome_cenario} ---")
    print(f"Melhor rota: {historico['melhor_rota']}")
    print(f"Distância da melhor rota: {historico['melhor_distancia']:.2f}")
    print(f"Épocas executadas: {historico['total_epocas']}")
    print(f"Época da última melhoria: {historico['epoca_ultima_melhoria']}")
    print(f"Tempo total: {historico['tempo_total']:.2f} s")
    print(f"Tempo até a última melhoria: {historico['tempo_ultima_melhoria']:.2f} s")
    return historico


def comparar_com_otimo(historico, n, raio):
    otima = ag.distancia_otima_circulo(n, raio)
    encontrada = historico["melhor_distancia"]
    diferenca = encontrada - otima
    erro_percentual = diferenca / otima * 100

    print(f"Distância ótima teórica: {otima:.2f}")
    print(f"Diferença absoluta: {diferenca:.2f}")
    print(f"Erro percentual: {erro_percentual:.2f}%")
    return otima


def salvar_rota_da_epoca(nome_cenario, pontos, historico, epoca, nome_arquivo):
    individuo = historico["melhor_individuo"][epoca]
    distancia = historico["melhor_ate_agora"][epoca]
    titulo = f"{nome_cenario} | Época {epoca} | Distância: {distancia:.2f}"
    vis.salvar_rota(pontos, individuo, titulo, caminho_resultado(nome_arquivo))


def salvar_historico_csv(historico, nome_arquivo):
    """Guarda o desempenho e a melhor rota de TODAS as épocas."""
    with open(caminho_resultado(nome_arquivo), "w", newline="") as arquivo:
        escritor = csv.writer(arquivo)
        escritor.writerow(["epoca", "melhor_da_epoca", "melhor_ate_agora", "media", "melhor_rota"])
        for i in historico["epocas"]:
            rota = " ".join(str(cidade) for cidade in historico["melhor_individuo"][i])
            escritor.writerow([i, f"{historico['melhor_da_epoca'][i]:.4f}",
                               f"{historico['melhor_ate_agora'][i]:.4f}",
                               f"{historico['media'][i]:.4f}", rota])


# ---------------------------------------------------------------------------
# Experimentos
# ---------------------------------------------------------------------------

def experimento_aleatorio():
    random.seed(SEED)
    nome = "Aleatório"
    pontos = ag.gerar_pontos_aleatorios(N_POINTS_RANDOM)
    historico = resolver(nome, pontos, MAX_GENERATIONS, MAX_STAGNATION)

    salvar_rota_da_epoca(nome, pontos, historico, 0, "aleatorio_rota_inicial.png")
    salvar_rota_da_epoca(nome, pontos, historico, historico["total_epocas"], "aleatorio_rota_final.png")
    vis.salvar_convergencia(historico, f"Convergência - cenário aleatório ({N_POINTS_RANDOM} pontos)",
                            caminho_resultado("aleatorio_convergencia.png"), manter_aberto=MOSTRAR_JANELA)
    salvar_historico_csv(historico, "aleatorio_historico.csv")


def experimento_circular():
    random.seed(SEED)
    nome = "Círculo"
    pontos = ag.gerar_pontos_circulo(N_POINTS_CIRCLE, CIRCLE_RADIUS)
    historico = resolver(nome, pontos, MAX_GENERATIONS, MAX_STAGNATION)
    otima = comparar_com_otimo(historico, N_POINTS_CIRCLE, CIRCLE_RADIUS)

    salvar_rota_da_epoca(nome, pontos, historico, 0, "circular_rota_inicial.png")
    salvar_rota_da_epoca(nome, pontos, historico, historico["total_epocas"], "circular_rota_final.png")
    vis.salvar_convergencia(historico, f"Convergência - cenário circular ({N_POINTS_CIRCLE} pontos)",
                            caminho_resultado("circular_convergencia.png"), otima, MOSTRAR_JANELA)
    salvar_historico_csv(historico, "circular_historico.csv")


def experimento_bonus():
    random.seed(SEED)
    nome = "Bônus círculo"
    pontos = ag.gerar_pontos_circulo(N_POINTS_BONUS, CIRCLE_RADIUS)
    historico = resolver(nome, pontos, MAX_GENERATIONS_BONUS, MAX_STAGNATION_BONUS)
    otima = comparar_com_otimo(historico, N_POINTS_BONUS, CIRCLE_RADIUS)

    # Snapshots intermediários: só das épocas que realmente aconteceram
    for epoca in BONUS_SNAPSHOT_EPOCHS:
        if epoca <= historico["total_epocas"]:
            salvar_rota_da_epoca(nome, pontos, historico, epoca, f"bonus_epoca_{epoca}.png")
    salvar_rota_da_epoca(nome, pontos, historico, historico["total_epocas"], "bonus_final.png")
    vis.salvar_convergencia(historico, f"Convergência - bônus circular ({N_POINTS_BONUS} pontos)",
                            caminho_resultado("bonus_convergencia.png"), otima, MOSTRAR_JANELA)


if __name__ == "__main__":
    os.makedirs(PASTA_RESULTADOS, exist_ok=True)
    experimento_aleatorio()
    experimento_circular()
    experimento_bonus()

    if MOSTRAR_JANELA:
        vis.manter_janelas_abertas()
