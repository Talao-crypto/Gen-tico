import matplotlib.pyplot as plt

# Janela usada para mostrar a rota enquanto o algoritmo roda
janela_figura = None
janela_eixo = None


def desenhar_rota(eixo, pontos, rota, titulo):
    eixo.clear()

    # Linhas entre as cidades, na ordem da rota
    xs = []
    ys = []
    for cidade in rota:
        xs.append(pontos[cidade][0])
        ys.append(pontos[cidade][1])
    eixo.plot(xs, ys, "-", color="blue")

    # Linha tracejada de volta para a cidade inicial
    eixo.plot([xs[-1], xs[0]], [ys[-1], ys[0]], "--", color="blue")

    # As cidades (a inicial em laranja)
    for x, y in pontos:
        eixo.plot(x, y, "o", color="black", markersize=4)
    eixo.plot(xs[0], ys[0], "o", color="orange", markersize=8)

    eixo.set_title(titulo)
    eixo.set_aspect("equal")


def salvar_rota(pontos, rota, titulo, caminho):
    figura, eixo = plt.subplots(figsize=(6, 6))
    desenhar_rota(eixo, pontos, rota, titulo)
    figura.savefig(caminho)
    plt.close(figura)


def abrir_janela(nome_cenario):
    global janela_figura, janela_eixo
    plt.ion()
    janela_figura, janela_eixo = plt.subplots(figsize=(6, 6))
    janela_figura.suptitle(nome_cenario)


def atualizar_janela(pontos, epoca, rota, distancia):
    desenhar_rota(janela_eixo, pontos, rota, f"Época {epoca} | Melhor: {distancia:.2f}")
    plt.pause(0.001)


def salvar_convergencia(historico, titulo, caminho, distancia_otima=None):
    epocas = range(len(historico["melhores"]))

    figura, eixo = plt.subplots(figsize=(8, 5))
    eixo.plot(epocas, historico["melhores"], label="Melhor distância")
    eixo.plot(epocas, historico["medias"], label="Distância média da população")
    if distancia_otima is not None:
        eixo.axhline(distancia_otima, color="gray", linestyle="--",
                     label=f"Ótimo teórico ({distancia_otima:.2f})")

    eixo.set_title(titulo)
    eixo.set_xlabel("Época")
    eixo.set_ylabel("Distância")
    eixo.legend()
    figura.savefig(caminho)
    # A figura fica aberta para aparecer em plt.show() quando houver janela


def mostrar_janelas():
    plt.ioff()
    plt.show()
