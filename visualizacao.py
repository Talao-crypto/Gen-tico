import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, PillowWriter


def desenhar_rota(pontos, rota, titulo):
    # Linhas entre as cidades, na ordem da rota
    xs = []
    ys = []
    for cidade in rota:
        xs.append(pontos[cidade][0])
        ys.append(pontos[cidade][1])
    plt.plot(xs, ys, "-", color="blue")

    # Linha tracejada de volta para a cidade inicial
    plt.plot([xs[-1], xs[0]], [ys[-1], ys[0]], "--", color="blue")

    # As cidades (a inicial em laranja)
    for x, y in pontos:
        plt.plot(x, y, "o", color="black", markersize=4)
    plt.plot(xs[0], ys[0], "o", color="orange", markersize=8)

    plt.title(titulo)
    plt.axis("equal")


def salvar_rota(pontos, rota, titulo, caminho):
    plt.figure(figsize=(6, 6))
    desenhar_rota(pontos, rota, titulo)
    plt.savefig(caminho)
    plt.close()


def salvar_animacao(pontos, historico, nome, caminho, passo=1):
    """GIF com a melhor rota a cada `passo` épocas (passo=1: todas as épocas)."""
    ultima_epoca = len(historico["melhores"]) - 1
    epocas = list(range(0, ultima_epoca + 1, passo))
    if epocas[-1] != ultima_epoca:
        epocas.append(ultima_epoca)

    figura = plt.figure(figsize=(5, 5))

    def desenhar_quadro(epoca):
        plt.clf()
        distancia = historico["melhores"][epoca]
        desenhar_rota(pontos, historico["rotas"][epoca],
                      f"{nome} | Época {epoca} | Distância: {distancia:.2f}")

    animacao = FuncAnimation(figura, desenhar_quadro, frames=epocas)
    animacao.save(caminho, writer=PillowWriter(fps=10), dpi=70)
    plt.close(figura)


def atualizar_janela(pontos, epoca, rota, distancia):
    plt.ion()
    plt.figure("Rota ao vivo", figsize=(6, 6))
    plt.clf()
    desenhar_rota(pontos, rota, f"Época {epoca} | Melhor: {distancia:.2f}")
    plt.pause(0.001)


def salvar_convergencia(historico, titulo, caminho, distancia_otima=None):
    plt.figure(figsize=(8, 5))
    plt.plot(historico["melhores"], label="Melhor distância")
    plt.plot(historico["medias"], label="Distância média da população")
    if distancia_otima is not None:
        plt.axhline(distancia_otima, color="gray", linestyle="--",
                    label=f"Ótimo teórico ({distancia_otima:.2f})")

    plt.title(titulo)
    plt.xlabel("Época")
    plt.ylabel("Distância")
    plt.legend()
    plt.savefig(caminho)
    # A figura fica aberta para aparecer em plt.show() quando houver janela


def mostrar_janelas():
    plt.ioff()
    plt.show()
