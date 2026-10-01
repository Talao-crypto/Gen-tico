import matplotlib.pyplot as plt

COR_ROTA = "#2a78d6"
COR_MEDIA = "#eb6834"
COR_PONTOS = "#333333"
COR_REFERENCIA = "#777777"


def desenhar_rota(ax, pontos, individuo, titulo):
    ax.clear()

    # Linhas na ordem do indivíduo
    xs = [pontos[cidade][0] for cidade in individuo]
    ys = [pontos[cidade][1] for cidade in individuo]
    ax.plot(xs, ys, "-", color=COR_ROTA, linewidth=1.5)

    # Volta da última cidade para a primeira (fecha o ciclo)
    primeira, ultima = pontos[individuo[0]], pontos[individuo[-1]]
    ax.plot([ultima[0], primeira[0]], [ultima[1], primeira[1]], "--", color=COR_ROTA,
            linewidth=1.5, label="Volta para o início")

    ax.scatter([p[0] for p in pontos], [p[1] for p in pontos], color=COR_PONTOS, s=25, zorder=3)
    ax.scatter([primeira[0]], [primeira[1]], color=COR_MEDIA, s=60, zorder=4, label="Cidade inicial")

    ax.set_title(titulo)
    ax.set_aspect("equal")
    ax.grid(True, alpha=0.3)
    ax.legend(loc="upper right", fontsize=8)


def salvar_rota(pontos, individuo, titulo, caminho):
    fig, ax = plt.subplots(figsize=(6, 6))
    desenhar_rota(ax, pontos, individuo, titulo)
    fig.savefig(caminho, dpi=120, bbox_inches="tight")
    plt.close(fig)


def criar_janela_ao_vivo(pontos, nome_cenario):
    """Abre uma janela e devolve a função que o AG chama para redesenhar a melhor rota."""
    plt.ion()
    fig, ax = plt.subplots(figsize=(6, 6))

    def atualizar(epoca, individuo, distancia):
        titulo = f"{nome_cenario} | Época {epoca} | Melhor: {distancia:.2f}"
        desenhar_rota(ax, pontos, individuo, titulo)
        fig.canvas.draw_idle()
        plt.pause(0.001)

    return atualizar


def salvar_convergencia(historico, titulo, caminho, distancia_otima=None, manter_aberto=False):
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(historico["epocas"], historico["melhor_ate_agora"], color=COR_ROTA, linewidth=2,
            label="Melhor distância encontrada", zorder=3)
    ax.plot(historico["epocas"], historico["media"], color=COR_MEDIA, linewidth=1.5,
            label="Distância média da população")
    if distancia_otima is not None:
        ax.axhline(distancia_otima, color=COR_REFERENCIA, linestyle="--", linewidth=1.5,
                   label=f"Ótimo teórico ({distancia_otima:.2f})")

    ax.set_title(titulo)
    ax.set_xlabel("Época")
    ax.set_ylabel("Distância")
    ax.grid(True, alpha=0.3)
    ax.legend()
    fig.savefig(caminho, dpi=120, bbox_inches="tight")

    if not manter_aberto:
        plt.close(fig)


def manter_janelas_abertas():
    plt.ioff()
    plt.show()
