# Algoritmo Genético para o Caixeiro Viajante

Trabalho de **Sistemas Inteligentes e Aprendizado de Máquina**. O programa procura o menor caminho que passa por todas as cidades uma única vez e volta à cidade inicial, usando um algoritmo genético escrito do zero (só `random`, `math`, `time`, `csv` e `matplotlib`).

## Como executar

```bash
pip install -r requirements.txt

python testes.py                # testes do algoritmo
python main.py                  # 3 experimentos, com janela mostrando a melhor rota
python main.py --sem-janela     # mesmos experimentos, só salva os resultados em resultados/
python comparar_parametros.py   # experimento extra: mutação e tamanho da população
```

## Arquivos

| Arquivo | O que tem |
|---|---|
| `algoritmo_genetico.py` | O algoritmo: pontos, população, distância, cruzamento, mutação e o loop das gerações |
| `main.py` | Parâmetros no topo e os 3 experimentos (aleatório, círculo e bônus) |
| `visualizacao.py` | Desenho das rotas e do gráfico de convergência |
| `comparar_parametros.py` | Compara taxas de mutação e tamanhos de população |
| `testes.py` | Testes com `assert` |
| `resultados/` | Imagens, gráficos e CSV gerados pelo `main.py` |

## Como o algoritmo funciona

**Problema.** Dados `n` pontos (mínimo 8) com coordenadas `(x, y)`, achar a ordem de visita de menor distância total. A distância entre dois pontos é a euclidiana, `sqrt((x2-x1)² + (y2-y1)²)`, e o caminho é fechado (volta ao início).

**Indivíduo.** Uma lista com a ordem das cidades, por exemplo `[3, 0, 2, 1]`. Cada cidade aparece uma vez, então todo indivíduo é uma rota válida.

**Aptidão.** É a distância total da rota, somando a volta da última cidade para a primeira. Quanto **menor**, melhor.

**Passo a passo** (`executar_algoritmo_genetico`):

1. Cria a população inicial com rotas embaralhadas (época 0).
2. Calcula a distância de cada indivíduo e ordena do melhor para o pior.
3. Guarda os dados da época e verifica se deve parar.
4. **Seleção Top Ranking:** só os melhores (`TAXA_SELECAO`, 50%) podem ser pais.
5. **Elitismo:** o melhor indivíduo passa direto para a próxima geração.
6. Até completar a população: sorteia dois pais, faz o **Ordered Crossover** e, com chance `TAXA_MUTACAO`, aplica a **mutação Swap**.
7. A nova geração substitui a antiga e volta ao passo 2.

**Ordered Crossover.** Sorteia dois cortes, copia o trecho do pai 1 para o filho **na mesma posição** e preenche o resto com as cidades que faltam, na ordem em que aparecem no pai 2:

```
pai 1: [0, 1, 2, 3, 4, 5, 6, 7]   trecho (posições 2 a 4): [2, 3, 4]
pai 2: [4, 6, 1, 0, 7, 3, 5, 2]   sem 2, 3 e 4: [6, 1, 0, 7, 5]
filho: [6, 1, 2, 3, 4, 0, 7, 5]
```

O filho nunca repete cidades. Manter o trecho na mesma posição é importante: com pais iguais, o filho sai igual aos pais.

**Mutação Swap.** Troca duas cidades de lugar, o que mantém a rota válida.

**Parada.** O algoritmo para no primeiro destes casos: chegou a `MAX_GERACOES` ou ficou `MAX_ESTAGNACAO` épocas sem melhorar a melhor distância.

## Experimentos (`main.py`)

Todos os parâmetros ficam no topo do arquivo. Cada experimento começa com `random.seed(SEED)`, então os resultados se repetem a cada execução.

| Experimento | Pontos | O que mostra |
|---|---|---|
| Aleatório | 20 pontos em um quadrado 100 × 100 | Funcionamento geral do algoritmo |
| Círculo | 20 pontos num círculo de raio 40 | Compara com a distância ótima conhecida: `n · 2 · R · sin(π/n)` |
| Bônus | 100 pontos no círculo | Como o algoritmo se comporta com muitos pontos (usa mais épocas) |

Para cada um o programa imprime a melhor rota, a distância, as épocas, os tempos e (nos círculos) a diferença para o ótimo. Em `resultados/` ficam as imagens das rotas, o gráfico de convergência e `*_historico.csv` com a melhor distância, a média e a melhor rota de cada época.

Rode `python main.py --sem-janela` para ver os números atuais. Eles dependem da seed e do código, e os tempos dependem da máquina.

## Comparação de parâmetros (`comparar_parametros.py`)

Roda o círculo de 20 pontos com 10 seeds diferentes para cada configuração e mostra quantas vezes o ótimo foi encontrado, o erro médio, as épocas e o tempo. Varia a taxa de mutação (0% a 100%) e o tamanho da população (20 a 500). Leva cerca de 30 segundos.

## Testes (`testes.py`)

Verificam: população com permutações válidas, distância com volta ao início, ótimo do círculo, mínimo de 8 pontos, ordenação, Ordered Crossover (incluindo o exemplo da aula e a ausência de cidades repetidas), mutação Swap, elitismo, tamanho fixo da população, as duas formas de parada e a reprodutibilidade por seed.
