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

## Justificativa das escolhas

Os números citados aqui vêm de `resultados/*_historico.csv` (gerados pelo `main.py`) e da tabela do `comparar_parametros.py`, mostrada na seção [Resultados](#resultados).

### Representação do gene

Cada indivíduo é uma **permutação** das cidades: `[3, 0, 2, 1]` significa "visite a cidade 3, depois a 0, depois a 2, depois a 1 e volte à 3". Cada gene é uma cidade, e a posição do gene é a ordem da visita.

Escolhemos essa representação porque ela só gera **rotas válidas**. O problema exige visitar cada cidade exatamente uma vez, e uma permutação já garante isso por construção. Outras opções teriam problemas:

- **Binária** (cada cidade codificada em bits): a maioria das cadeias de bits não representa uma rota válida (cidades repetidas ou faltando). Seria preciso consertar ou descartar indivíduos a cada geração.
- **Coordenadas ou pesos reais** (ordenar cidades por uma chave aleatória): funciona, mas é indireta. O cruzamento passa a mexer em números que não têm relação clara com a rota.

Com a permutação, o que o algoritmo manipula é a própria rota, e a aptidão é calculada direto dela.

Uma observação: como o caminho é cíclico, a mesma rota tem várias representações (`[0, 1, 2]`, `[1, 2, 0]` e `[2, 0, 1]` são o mesmo ciclo). Isso não atrapalha, porque a distância é igual. Por isso a melhor rota do círculo aparece como `15 16 17 18 19 0 1 2 ... 14`, que é o círculo em ordem começando da cidade 15.

### Cruzamento

Usamos o **Ordered Crossover (OX)**. O cruzamento comum de um ponto não serve para permutações: juntar o começo de um pai com o fim do outro quase sempre repete cidades. Por exemplo, `[0, 1, 2 | 3]` com `[3, 2, 1 | 0]` daria `[0, 1, 2, 0]`.

O OX foi escolhido porque:

1. **Sempre gera uma rota válida.** O trecho vem do pai 1, e o resto é preenchido só com as cidades que faltam, na ordem do pai 2.
2. **Preserva o que importa no caixeiro viajante:** a **ordem relativa** e as cidades **vizinhas**. O trecho copiado do pai 1 é um pedaço de rota inteiro, com as mesmas ligações entre cidades. As cidades vindas do pai 2 mantêm a ordem em que ele as visitava. Assim, bons pedaços de caminho passam dos pais para os filhos.
3. **Mantém o trecho na mesma posição.** Se os dois pais são iguais, o filho é igual a eles. Isso evita que o cruzamento destrua uma boa solução quando a população já convergiu.

O trecho tem cortes sorteados a cada cruzamento, então o tamanho do pedaço herdado de cada pai varia.

### Seleção e elitismo

- **Seleção Top Ranking (`TAXA_SELECAO = 0.5`):** só a metade melhor da população pode ser pai. É simples, e como a lista já está ordenada pela aptidão, não precisa de nenhum cálculo extra. Usar 50% (e não, por exemplo, 10%) mantém pais suficientes para a população não ficar parecida rápido demais.
- **Elitismo (1 indivíduo):** o melhor passa intacto para a próxima geração. Isso garante que a melhor distância **nunca piora** de uma época para a outra, o que dá para ver nos gráficos de convergência (a linha "Melhor distância" só desce ou fica parada). Guardamos só um para não diminuir a diversidade.

### Função de aptidão

A aptidão é a **distância total da rota**, somando a distância euclidiana entre cada cidade e a próxima e **incluindo a volta da última cidade para a primeira**:

```
aptidão(rota) = Σ sqrt((x[i+1] - x[i])² + (y[i+1] - y[i])²),   com i+1 = 0 na última cidade
```

Escolhemos assim porque essa é exatamente a grandeza que o problema pede para minimizar: um caminho cíclico, com distância euclidiana. Não há penalidades, porque a representação nunca gera rotas inválidas.

A aptidão é **minimizada** (menor = melhor). Muitos algoritmos genéticos usam `1 / distância` para transformar o problema em maximização, mas isso só é necessário na seleção por roleta, em que a chance de cada indivíduo depende do valor. Como usamos Top Ranking, só a **ordem** importa, então a distância pode ser usada direto. Isso também deixa os resultados mais fáceis de ler, porque o valor da aptidão é a própria distância.

### Tamanho da população

Usamos `TAMANHO_POPULACAO = 100`. A população precisa ser grande o bastante para ter diversidade (rotas diferentes para combinar) e pequena o bastante para cada época ser rápida.

A comparação com 10 seeds no círculo de 20 pontos mostra o efeito:

- **20 indivíduos:** pequena demais. Não achou o ótimo nenhuma vez (erro médio de 76%), porque a população fica igual muito rápido e o algoritmo para.
- **50 e 100 indivíduos:** acharam o ótimo em 8 das 10 execuções, em cerca de 0,2 s.
- **200 e 500 indivíduos:** acharam o ótimo nas 10 execuções. Com 500, o tempo médio triplica (1,06 s contra 0,36 s com 200) sem ganho de qualidade.

O valor 100 foi um compromisso entre qualidade e tempo. Os dados mostram que **200 também seria uma boa escolha**: acerta sempre, precisa de menos épocas (141 contra 192) e ainda leva menos de meio segundo. Acima disso, o custo cresce e não há ganho.

### Taxa de mutação

A mutação **Swap** troca duas cidades de lugar. Ela é aplicada ao filho inteiro com probabilidade `TAXA_MUTACAO` (não a cada gene). Usamos `TAXA_MUTACAO = 0.05`.

A mutação serve para trazer **diversidade**: o cruzamento só recombina ligações que já existem na população, e a mutação cria ligações novas. A comparação mostra os dois extremos:

- **0%:** achou o ótimo em só 1 das 10 execuções (erro médio de 32%). Sem mutação, a população fica parecida, o OX com pais iguais gera filhos iguais, e o algoritmo fica preso no primeiro bom resultado que encontra (convergência prematura).
- **100%:** pior resultado de todos (0/10, erro médio de 85%). Como todo filho sofre uma troca, quase toda rota boa é estragada na geração seguinte. Só o elitismo segura o melhor, e a população não consegue acumular bons trechos.
- **Entre esses extremos:** 1% acertou 5/10, 5% acertou 8/10, e **20% e 50% acertaram 10/10**.

Partimos de 5%, um valor comum na literatura (que costuma usar entre 1% e 10%). A comparação mostrou que, neste problema, o ideal é uma taxa **mais alta, por volta de 20%**. Isso faz sentido porque aqui a taxa vale para o indivíduo inteiro e cada mutação troca só duas cidades. A mutação é fraca, então pode acontecer mais vezes. 20% é melhor que 50% por ficar mais longe do extremo destrutivo de 100%.

### Critério de parada

O algoritmo para no que acontecer primeiro:

1. **Estagnação (`MAX_ESTAGNACAO = 100`):** 100 épocas seguidas sem melhorar a melhor distância. É o critério principal. Como não sabemos a resposta certa no cenário aleatório, não dá para parar ao "acertar". Paramos quando o algoritmo deixa de progredir. Escolhemos 100 porque nas execuções a última melhoria acontece bem antes disso, e 100 épocas dão chance de a mutação tirar a população de um ponto parado antes de desistir.
2. **Limite de épocas (`MAX_GERACOES = 500`):** é uma trava de segurança, para o programa nunca rodar sem fim. Nos experimentos com 20 pontos ela nem chega a ser usada: o aleatório parou na época 193 e o círculo na 227, os dois por estagnação.

Uma melhora só conta se for maior que `1e-9`, para que diferenças de arredondamento de ponto flutuante não reiniciem a contagem de estagnação.

No **bônus** (100 pontos) os limites são maiores (`MAX_GERACOES_BONUS = 20000`, `MAX_ESTAGNACAO_BONUS = 2000`). Com mais cidades há muito mais rotas possíveis, cada melhora é mais rara, e 100 épocas sem melhora não indicam que o algoritmo terminou de progredir.

## Experimentos (`main.py`)

Todos os parâmetros ficam no topo do arquivo. Cada experimento começa com `random.seed(SEED)`, então os resultados se repetem a cada execução.

| Experimento | Pontos | O que mostra |
|---|---|---|
| Aleatório | 20 pontos em um quadrado 100 × 100 | Funcionamento geral do algoritmo |
| Círculo | 20 pontos num círculo de raio 40 | Compara com a distância ótima conhecida: `n · 2 · R · sin(π/n)` |
| Bônus | 100 pontos no círculo | Como o algoritmo se comporta com muitos pontos (usa mais épocas) |

Para cada um o programa imprime a melhor rota, a distância, as épocas, os tempos e (nos círculos) a diferença para o ótimo. Em `resultados/` ficam as imagens das rotas, o gráfico de convergência e `*_historico.csv` com a melhor distância, a média e a melhor rota de cada época.

Rode `python main.py --sem-janela` para ver os números atuais. Eles dependem da seed e do código, e os tempos dependem da máquina. Os números da execução que gerou os arquivos de `resultados/` estão na seção [Resultados](#resultados).

## Comparação de parâmetros (`comparar_parametros.py`)

Roda o círculo de 20 pontos com 10 seeds diferentes para cada configuração e mostra quantas vezes o ótimo foi encontrado, o erro médio, as épocas e o tempo. Varia a taxa de mutação (0% a 100%) e o tamanho da população (20 a 500). Leva cerca de 30 segundos.

## Resultados

### Cenário aleatório (20 pontos)

Arquivos: `resultados/aleatorio_*.png` e `resultados/aleatorio_historico.csv`.

| Época | Melhor distância | Média da população |
|---|---|---|
| 0 (população inicial) | 815,40 | 1081,46 |
| 1 | 751,17 | 1007,93 |
| 193 (última) | 352,32 | 358,12 |

- Melhor rota: `11 4 0 9 3 12 19 14 18 10 15 2 7 16 17 8 5 6 13 1`
- A distância caiu 57% em relação à melhor rota aleatória inicial.
- Última melhoria na época 93; parou na 193 por estagnação.
- Não existe ótimo conhecido para comparar. Nas imagens a rota final não tem cruzamentos, o que é um sinal de boa solução (uma rota com cruzamento sempre pode ser encurtada).

### Cenário circular (20 pontos, raio 40)

Arquivos: `resultados/circular_*.png` e `resultados/circular_historico.csv`.

- Ótimo teórico: `20 · 2 · 40 · sin(π/20)` = **250,30**
- Distância encontrada: **250,30**, ou seja, erro de **0%**. O algoritmo achou o ótimo.
- Melhor rota: `15 16 17 18 19 0 1 2 ... 14`, que é o círculo percorrido em ordem.
- Última melhoria na época 127; parou na 227 por estagnação.

### Bônus (100 pontos no círculo)

Arquivos: `resultados/bonus_*.png` e `resultados/bonus_historico.csv`.

Ótimo teórico: `100 · 2 · 40 · sin(π/100)` = **251,29**

| Época | Melhor distância | Erro para o ótimo |
|---|---|---|
| 0 | 4496,30 | 1689% |
| 10 | 3799,61 | 1412% |
| 50 | 2711,65 | 979% |
| 100 | 2055,43 | 718% |
| 500 | 1239,92 | 393% |
| 1000 | 1048,44 | 317% |
| 2000 | 938,96 | 274% |
| 5000 | 695,65 | 177% |
| 7000 | 690,24 | 175% |
| 9182 (última) | 680,51 | 171% |

- Última melhoria na época 7182; parou na 9182 por estagnação (2000 épocas sem melhorar).
- Tempo total e tempo até a última melhoria: _preencher com a saída de `python main.py --sem-janela`_ (o tempo depende da máquina).

Com 100 pontos o algoritmo **não chegou ao ótimo**: a rota final tem 171% de erro. A melhora é muito rápida no começo (a distância cai pela metade nas primeiras 100 épocas) e depois fica cada vez mais lenta. Entre a época 5000 e a 9182 o ganho foi só de 2%. Isso mostra a principal limitação do algoritmo genético simples em problemas grandes:

- O número de rotas possíveis cresce com o fatorial do número de cidades (100! é cerca de 10¹⁵⁸), então a busca é muito mais difícil.
- A mutação Swap troca duas cidades distantes de lugar e quase sempre piora uma rota que já é boa. Ela não consegue "desfazer" um cruzamento entre arestas, que é o que falta para melhorar uma rota quase pronta.
- Formas de melhorar (não implementadas): população maior, taxa de mutação mais alta, mutação por **inversão** de um trecho (que desfaz cruzamentos) ou uma busca local como o **2-opt** aplicada às melhores rotas.

### Comparação de parâmetros

Saída de `python comparar_parametros.py` (círculo de 20 pontos, 10 seeds por configuração; os tempos dependem da máquina):

| População | Mutação | Achou o ótimo | Erro médio | Épocas (média) | Tempo (média) |
|---|---|---|---|---|---|
| 100 | 0% | 1/10 | 31,68% | 135 | 0,190 s |
| 100 | 1% | 5/10 | 17,41% | 178 | 0,267 s |
| 100 | 5% | 8/10 | 11,48% | 192 | 0,233 s |
| 100 | 20% | 10/10 | 0,00% | 164 | 0,209 s |
| 100 | 50% | 10/10 | 0,00% | 206 | 0,273 s |
| 100 | 100% | 0/10 | 84,76% | 259 | 0,385 s |
| 20 | 5% | 0/10 | 75,99% | 293 | 0,075 s |
| 50 | 5% | 8/10 | 7,29% | 276 | 0,165 s |
| 200 | 5% | 10/10 | 0,00% | 141 | 0,363 s |
| 500 | 5% | 10/10 | 0,00% | 162 | 1,064 s |

## Testes (`testes.py`)

Verificam: população com permutações válidas, distância com volta ao início, ótimo do círculo, mínimo de 8 pontos, ordenação, Ordered Crossover (incluindo o exemplo da aula e a ausência de cidades repetidas), mutação Swap, elitismo, tamanho fixo da população, as duas formas de parada e a reprodutibilidade por seed.
