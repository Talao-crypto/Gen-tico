# Algoritmo Genético para o Caixeiro Viajante

Trabalho de **Sistemas Inteligentes e Aprendizado de Máquina**. O programa procura o menor caminho que passa por todas as cidades uma única vez e volta à cidade inicial, usando um algoritmo genético escrito do zero (só `random`, `math`, `time`, `csv` e `matplotlib`).

## Como executar

```bash
pip install -r requirements.txt

python testes.py                # testes do algoritmo
python main.py                  # 3 experimentos, com janela mostrando a melhor rota a cada época
python main.py --sem-janela     # mesmos experimentos, só salva os resultados em resultados/
python comparar_parametros.py           # experimento extra: tipo/taxa de mutação e população (~1 min)
python comparar_parametros.py --bonus   # o mesmo, mais o teste das taxas com 100 pontos (~15 min)
```

## Arquivos

| Arquivo | O que tem |
|---|---|
| `algoritmo_genetico.py` | O algoritmo: pontos, população, distância, cruzamento, mutação e o loop das gerações |
| `main.py` | Parâmetros no topo e os 3 experimentos (aleatório, círculo e bônus) |
| `visualizacao.py` | Desenho das rotas, janela ao vivo, animação (GIF) e gráfico de convergência |
| `comparar_parametros.py` | Compara tipos e taxas de mutação e tamanhos de população |
| `testes.py` | Testes com `assert` |
| `resultados/` | Imagens, GIFs, gráficos, CSV e resumos gerados pelo `main.py` |

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
6. Até completar a população: sorteia dois pais, faz o **Ordered Crossover** e, com chance `TAXA_MUTACAO`, aplica a **mutação por inversão**.
7. A nova geração substitui a antiga e volta ao passo 2.

**Ordered Crossover.** Sorteia dois cortes, copia o trecho do pai 1 para o filho **na mesma posição** e preenche o resto com as cidades que faltam, na ordem em que aparecem no pai 2:

```
pai 1: [0, 1, 2, 3, 4, 5, 6, 7]   trecho (posições 2 a 4): [2, 3, 4]
pai 2: [4, 6, 1, 0, 7, 3, 5, 2]   sem 2, 3 e 4: [6, 1, 0, 7, 5]
filho: [6, 1, 2, 3, 4, 0, 7, 5]
```

O filho nunca repete cidades. Manter o trecho na mesma posição é importante: com pais iguais, o filho sai igual aos pais.

**Mutação por inversão.** Sorteia um trecho da rota e inverte a ordem dele, o que mantém a rota válida:

```
antes:  [0, 1, 2, 3, 4, 5]   trecho (posições 1 a 4): [1, 2, 3, 4]
depois: [0, 4, 3, 2, 1, 5]
```

O código também tem a **mutação Swap** (troca duas cidades de lugar), usada só para comparação (`TIPO_MUTACAO` no `main.py`).

**Parada.** O algoritmo para no primeiro destes casos: chegou a `MAX_GERACOES` ou ficou `MAX_ESTAGNACAO` épocas sem melhorar a melhor distância.

## Justificativa das escolhas

Os números citados aqui vêm de `resultados/` (gerados pelo `main.py`) e das tabelas do `comparar_parametros.py`, mostradas na seção [Resultados](#resultados). Para não tirar conclusões de uma execução com sorte ou azar, cada configuração foi testada com várias seeds.

### Representação do gene

Cada indivíduo é uma **permutação** das cidades: `[3, 0, 2, 1]` significa "visite a cidade 3, depois a 0, depois a 2, depois a 1 e volte à 3". Cada gene é uma cidade, e a posição do gene é a ordem da visita.

Escolhemos essa representação porque ela só gera **rotas válidas**. O problema exige visitar cada cidade exatamente uma vez, e uma permutação já garante isso por construção. Outras opções teriam problemas:

- **Binária** (cada cidade codificada em bits): a maioria das cadeias de bits não representa uma rota válida (cidades repetidas ou faltando). Seria preciso consertar ou descartar indivíduos a cada geração.
- **Coordenadas ou pesos reais** (ordenar cidades por uma chave aleatória): funciona, mas é indireta. O cruzamento passa a mexer em números que não têm relação clara com a rota.

Com a permutação, o que o algoritmo manipula é a própria rota, e a aptidão é calculada direto dela.

Uma observação: como o caminho é cíclico, a mesma rota tem várias representações (`[0, 1, 2]`, `[1, 2, 0]` e `[2, 0, 1]` são o mesmo ciclo). Isso não atrapalha, porque a distância é igual. Por isso a melhor rota do círculo aparece como `14 15 16 17 18 19 0 1 2 ... 13`, que é o círculo em ordem começando da cidade 14.

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

A comparação com 10 seeds no círculo de 20 pontos (mutação por inversão 5%) mostra o efeito:

| População | Achou o ótimo | Erro médio | Tempo médio |
|---|---|---|---|
| 20 | 4/10 | 16,86% | 0,10 s |
| 50 | 7/10 | 7,59% | 0,15 s |
| **100** | **9/10** | **0,98%** | **0,21 s** |
| 200 | 10/10 | 0,00% | 0,39 s |
| 500 | 10/10 | 0,00% | 1,08 s |

- **20 e 50 indivíduos:** pequenas demais. A população fica parecida rápido, o algoritmo para cedo e erra bastante.
- **100 indivíduos:** acerta em 9 de 10 execuções, e na que errou ficou a menos de 10% do ótimo.
- **200 e 500 indivíduos:** acertam sempre, mas cada época custa proporcionalmente mais. Com 500 o tempo é 5 vezes o de 100.

Escolhemos 100 como **compromisso entre qualidade e tempo**. É o menor tamanho com resultado quase perfeito. Dobrar para 200 tira o último erro, mas dobra o custo de cada época. Isso pesa no bônus: com 100 indivíduos ele já leva cerca de 50 s, e com 200 levaria perto do dobro. Usamos o mesmo tamanho nos três cenários para que os resultados possam ser comparados entre si.

### Tipo de mutação: inversão em vez de Swap

A mutação serve para trazer **diversidade**: o cruzamento só recombina ligações entre cidades que já existem na população, e a mutação cria ligações novas. Ela é aplicada ao filho inteiro com probabilidade `TAXA_MUTACAO` (não a cada gene).

Testamos dois tipos, ambos sempre geram rotas válidas:

- **Swap:** troca duas cidades de lugar. Muda até **quatro** ligações da rota, nas duas pontas de cada cidade trocada. Numa rota que já está boa, tirar duas cidades do lugar quase sempre piora a distância.
- **Inversão:** inverte a ordem de um trecho. Muda só **duas** ligações, nas pontas do trecho, e o trecho continua sendo percorrido pelas mesmas cidades vizinhas, só no sentido contrário. É exatamente a operação que **desfaz um cruzamento**: se duas linhas da rota se cruzam, inverter o trecho entre elas troca as duas linhas por outras duas que não se cruzam, e a rota fica mais curta. Para pontos no plano, uma rota com cruzamento nunca é a ótima.

A comparação favorece a inversão nos três cenários (todos com população 100 e taxa 5%):

| Cenário | Swap | Inversão |
|---|---|---|
| Círculo, 20 pontos (10 seeds) | ótimo em 8/10, erro médio 11,48%, pior 67,86% | ótimo em 9/10, erro médio 0,98%, pior 9,75% |
| Aleatório, 20 pontos (10 conjuntos de pontos) | distância média 420,77 | distância média 404,21 |
| Círculo, 100 pontos (3 seeds) | erro médio 115,11% | erro médio 16,34% |

Com a seed 42 do `main.py`, o bônus com Swap parou com 171% de erro e várias linhas cruzando o círculo. Com a inversão, chegou ao ótimo. Por isso a inversão é a mutação usada. O Swap continua no código só para essa comparação.

### Taxa de mutação

Usamos `TAXA_MUTACAO = 0.05` (5%). A comparação com 10 seeds no círculo de 20 pontos mostra os dois extremos:

- **0%:** achou o ótimo em só 1 das 10 execuções (erro médio de 32%). Sem mutação, a população fica parecida, o OX com pais iguais gera filhos iguais, e o algoritmo fica preso no primeiro bom resultado que encontra (**convergência prematura**).
- **100%:** nenhum acerto (erro médio de 70%). Como todo filho sofre mutação, quase toda rota boa é estragada na geração seguinte. Só o elitismo segura o melhor, e a população não consegue acumular bons trechos.
- **Entre os extremos** (inversão): 1% acertou 7/10, **5% acertou 9/10**, 20% e 50% acertaram 10/10.

Com só 20 pontos, taxas de 20% ou 50% seriam um pouco melhores. Mas a taxa tem que funcionar também com muitos pontos, e no círculo de 100 pontos (3 seeds) o resultado é outro:

| Taxa (inversão) | Erro médio | Pior erro |
|---|---|---|
| 2% | 35,61% | 71,12% |
| **5%** | **16,34%** | **35,08%** |
| 10% | 37,32% | 53,11% |
| 20% | 51,49% | 95,31% |

Com 100 cidades a rota é longa e uma boa solução tem muitos trechos certos. Uma taxa alta estraga esses trechos antes que eles se espalhem pela população: com 20%, o algoritmo parou em média na metade das épocas (5327 contra 9771) e com o triplo do erro. Uma taxa baixa demais (2%) volta ao problema da convergência prematura.

**5% é a taxa que funciona bem nas duas escalas:** é a melhor com 100 pontos e quase perfeita com 20 (9/10, e o pior erro ficou abaixo de 10%). Também está dentro da faixa comum na literatura, de 1% a 10%.

### Critério de parada

O algoritmo para no que acontecer primeiro:

1. **Estagnação (`MAX_ESTAGNACAO = 100`):** 100 épocas seguidas sem melhorar a melhor distância. É o critério principal. Como não sabemos a resposta certa no cenário aleatório, não dá para parar ao "acertar". Paramos quando o algoritmo deixa de progredir. Escolhemos 100 olhando o histórico: a **maior pausa entre duas melhorias** foi de 12 épocas no aleatório e de 44 no círculo (da época 77 à 121). Esperar 100 épocas dá mais que o dobro dessa folga para a mutação tirar a população de um ponto parado antes de desistir, sem gastar muito tempo depois que o algoritmo realmente parou de melhorar.
2. **Limite de épocas (`MAX_GERACOES = 500`):** é uma trava de segurança, para o programa nunca rodar sem fim. Nos experimentos ela nem chega a ser usada: o aleatório parou na época 184 e o círculo na 221, os dois por estagnação. No bônus o limite é 20000 e o algoritmo parou na época 7490.

Uma melhora só conta se for maior que `1e-9`, para que diferenças de arredondamento de ponto flutuante não reiniciem a contagem de estagnação.

No **bônus** (100 pontos) os limites são maiores (`MAX_GERACOES_BONUS = 20000`, `MAX_ESTAGNACAO_BONUS = 2000`). Com mais cidades há muito mais rotas possíveis, e cada melhora é mais rara. No histórico do bônus a maior pausa foi de **625 épocas** (da 4382 à 5007), e depois dela a distância ainda caiu até o ótimo. Com estagnação de 100, o algoritmo teria parado longe da solução. Os 2000 dão cerca de 3 vezes a maior pausa observada.

## Experimentos (`main.py`)

Todos os parâmetros ficam no topo do arquivo. Cada experimento começa com `random.seed(SEED)`, então os resultados se repetem a cada execução.

| Experimento | Pontos | O que mostra |
|---|---|---|
| Aleatório | 20 pontos em um quadrado 100 × 100 | Funcionamento geral do algoritmo |
| Círculo | 20 pontos num círculo de raio 40 | Compara com a distância ótima conhecida: `n · 2 · R · sin(π/n)` |
| Bônus | 100 pontos no círculo | Como o algoritmo se comporta com muitos pontos (usa mais épocas) |

Para cada um o programa imprime a melhor rota, a distância, as épocas, os tempos e (nos círculos) a diferença para o ótimo. Em `resultados/` ficam:

| Arquivo | O que tem |
|---|---|
| `*_resumo.txt` | Parâmetros, melhor rota, distância, épocas, tempos e erro para o ótimo |
| `*_historico.csv` | Melhor distância, média e melhor rota de **cada época** |
| `*_evolucao.gif` | Animação da melhor rota em **cada época** (a cada 100 no bônus) |
| `*_convergencia.png` | Gráfico da melhor distância e da média por época |
| `*_epoca_N.png` | A rota nas épocas 0, 10, 50, 100 e na última (no bônus também 500, 1000, 2000, 3000 e 5000) |

Rode `python main.py --sem-janela` para ver os números atuais. Eles dependem da seed e do código, e os tempos dependem da máquina. Os números da execução que gerou os arquivos de `resultados/` estão na seção [Resultados](#resultados).

## Comparação de parâmetros (`comparar_parametros.py`)

Roda cada configuração com várias seeds e mostra quantas vezes o ótimo foi encontrado, o erro médio, o pior erro, as épocas e o tempo. Compara:

- os tipos (Swap e inversão) e as taxas de mutação (0% a 100%) no círculo de 20 pontos, com 10 seeds;
- Swap e inversão em 10 conjuntos diferentes de 20 pontos aleatórios;
- o tamanho da população (20 a 500) no círculo de 20 pontos;
- com `--bonus`: as taxas de mutação no círculo de 100 pontos, com 3 seeds.

Leva cerca de 1 minuto, ou cerca de 15 minutos com `--bonus`. As tabelas estão na seção [Resultados](#resultados).

## Resultados

Todos os números abaixo são da execução de `python main.py --sem-janela` que gerou a pasta `resultados/` (seed 42). O resumo de cada cenário está em `resultados/<cenário>_resumo.txt`. Os tempos dependem da máquina e **não incluem** o tempo gasto desenhando a janela ao vivo, que é descontado para medir só o algoritmo.

**Como acompanhar a solução a cada época** (o enunciado pede isso para os dois cenários):

- **Durante a execução** (`python main.py`): a janela "Rota ao vivo" redesenha a melhor rota **em todas as épocas** nos cenários de 20 pontos (a cada 100 no bônus). O console imprime, para cada época, a melhor distância, a distância média da população e a melhor rota.
- **Depois da execução**, em `resultados/`:
  - `*_evolucao.gif`: animação com a melhor rota de **cada época** (a cada 100 no bônus).
  - `*_historico.csv`: melhor distância, distância média e melhor rota de **cada época**.
  - `*_convergencia.png`: gráfico da melhor distância e da média por época.
  - `*_epoca_N.png`: a rota em épocas escolhidas e na última.

### Cenário aleatório (20 pontos)

| Época | Melhor distância | Média da população |
|---|---|---|
| 0 (população inicial) | 710,50 | 1048,59 |
| 184 (última) | 360,68 | 362,46 |

- Melhor rota: `6 13 1 11 4 0 9 3 12 7 19 14 18 10 15 2 16 17 8 5`
- A distância caiu 49% em relação à melhor rota aleatória inicial.
- Última melhoria na época 84; parou na 184 por estagnação.
- Tempo total: 0,29 s; tempo até a última melhoria: 0,14 s.
- Não existe ótimo conhecido para comparar. A rota final não tem cruzamentos, mas também não é necessariamente a menor possível: o algoritmo genético encontra uma boa solução **local**, como o enunciado pede. Com outras seeds a distância muda um pouco (ver a comparação com 10 conjuntos de pontos aleatórios abaixo).

### Cenário circular (20 pontos, raio 40)

- Ótimo teórico: `20 · 2 · 40 · sin(π/20)` = **250,30**
- Distância encontrada: **250,30**, ou seja, erro de **0%**. O algoritmo achou o ótimo.
- Melhor rota: `14 15 16 17 18 19 0 1 2 ... 13`, que é o círculo percorrido em ordem.
- Distância na época 0: 815,40 (226% acima do ótimo).
- Última melhoria na época 121; parou na 221 por estagnação.
- Tempo total: 0,29 s; tempo até a última melhoria: 0,17 s.

### Bônus (100 pontos no círculo)

Ótimo teórico: `100 · 2 · 40 · sin(π/100)` = **251,29**

| Época | Melhor distância | Erro para o ótimo | Imagem |
|---|---|---|---|
| 0 | 4496,30 | 1689,3% | `bonus_epoca_0.png` |
| 10 | 3814,81 | 1418,1% | `bonus_epoca_10.png` |
| 50 | 2747,36 | 993,3% | `bonus_epoca_50.png` |
| 100 | 1838,03 | 631,4% | `bonus_epoca_100.png` |
| 500 | 825,88 | 228,7% | `bonus_epoca_500.png` |
| 1000 | 633,70 | 152,2% | `bonus_epoca_1000.png` |
| 2000 | 501,31 | 99,5% | `bonus_epoca_2000.png` |
| 3000 | 447,13 | 77,9% | `bonus_epoca_3000.png` |
| 5000 | 276,29 | 10,0% | `bonus_epoca_5000.png` |
| 7490 (última) | 251,29 | 0,0% | `bonus_epoca_7490.png` |

- **Tempo até a convergência** (última melhoria, na época 5490): **35,75 s**.
- Tempo total (até parar, na época 7490, depois de 2000 épocas sem melhora): 48,11 s.
- O algoritmo **encontrou o ótimo** também com 100 pontos.

A melhora é muito rápida no começo (a distância cai para menos da metade nas primeiras 100 épocas) e depois fica cada vez mais lenta: de 1000 até 5000 foram 4000 épocas para ir de 152% para 10% de erro. O número de rotas possíveis cresce com o fatorial do número de cidades (100! é cerca de 10¹⁵⁸), por isso o bônus precisa de muito mais épocas que os cenários de 20 pontos.

Essa execução com a seed 42 chegou ao ótimo, mas isso **não acontece sempre**: com as seeds 0, 1 e 2 o erro final foi de 10,0%, 4,0% e 35,1% (média de 16,3%, ver a tabela abaixo). Um algoritmo genético encontra uma boa solução local, sem garantia de achar a melhor. Ainda assim é muito melhor que a mutação Swap, que com a mesma seed 42 parou com **171% de erro** e várias linhas cruzando o círculo, e com as seeds 0, 1 e 2 teve erro médio de 115%.

### Comparação de parâmetros

Saída de `python comparar_parametros.py --bonus` (os tempos dependem da máquina). "Achou o ótimo" conta as execuções com erro menor que 0,01%.

**Círculo de 20 pontos, 10 seeds, população 100:**

| Mutação | Taxa | Achou o ótimo | Erro médio | Pior erro | Épocas (média) | Tempo (média) |
|---|---|---|---|---|---|---|
| swap | 0% | 1/10 | 31,68% | 69,52% | 135 | 0,17 s |
| swap | 1% | 5/10 | 17,41% | 65,75% | 178 | 0,24 s |
| swap | 5% | 8/10 | 11,48% | 67,86% | 192 | 0,27 s |
| swap | 20% | 10/10 | 0,00% | 0,00% | 164 | 0,25 s |
| swap | 50% | 10/10 | 0,00% | 0,00% | 206 | 0,29 s |
| swap | 100% | 0/10 | 84,76% | 113,30% | 259 | 0,43 s |
| inversão | 0% | 1/10 | 31,68% | 69,52% | 135 | 0,17 s |
| inversão | 1% | 7/10 | 12,77% | 61,77% | 215 | 0,28 s |
| **inversão** | **5%** | **9/10** | **0,98%** | **9,75%** | **173** | **0,26 s** |
| inversão | 20% | 10/10 | 0,00% | 0,00% | 172 | 0,23 s |
| inversão | 50% | 10/10 | 0,00% | 0,00% | 286 | 0,40 s |
| inversão | 100% | 0/10 | 70,44% | 109,88% | 280 | 0,45 s |

Com 0% as duas linhas são iguais, porque nenhuma mutação acontece.

**20 pontos aleatórios, 10 conjuntos de pontos diferentes, população 100** (sem ótimo conhecido; menor é melhor):

| Mutação | Taxa | Distância média | Pior distância |
|---|---|---|---|
| swap | 5% | 420,77 | 508,16 |
| swap | 20% | 417,83 | 469,14 |
| **inversão** | **5%** | **404,21** | **471,09** |
| inversão | 20% | 401,83 | 455,52 |

**Círculo de 20 pontos, 10 seeds, inversão 5%, variando a população:**

| População | Achou o ótimo | Erro médio | Pior erro | Épocas (média) | Tempo (média) |
|---|---|---|---|---|---|
| 20 | 4/10 | 16,86% | 46,84% | 302 | 0,10 s |
| 50 | 7/10 | 7,59% | 37,33% | 218 | 0,15 s |
| **100** | **9/10** | **0,98%** | **9,75%** | **173** | **0,21 s** |
| 200 | 10/10 | 0,00% | 0,00% | 150 | 0,39 s |
| 500 | 10/10 | 0,00% | 0,00% | 155 | 1,08 s |

**Círculo de 100 pontos, 3 seeds, população 100** (limites do bônus):

| Mutação | Taxa | Achou o ótimo | Erro médio | Pior erro | Épocas (média) | Tempo (média) |
|---|---|---|---|---|---|---|
| swap | 5% | 0/3 | 115,11% | 150,87% | 14557 | 95,26 s |
| inversão | 2% | 0/3 | 35,61% | 71,12% | 10949 | 72,38 s |
| **inversão** | **5%** | **0/3** | **16,34%** | **35,08%** | **9771** | **62,71 s** |
| inversão | 10% | 0/3 | 37,32% | 53,11% | 7706 | 48,43 s |
| inversão | 20% | 1/3 | 51,49% | 95,31% | 5327 | 33,83 s |

Com 20% uma das 3 execuções achou o ótimo, mas as outras duas ficaram com 59% e 95% de erro. Por isso a média é bem pior que a de 5%.

## Testes (`testes.py`)

Verificam: população com permutações válidas, distância com volta ao início, ótimo do círculo, mínimo de 8 pontos, ordenação, Ordered Crossover (incluindo o exemplo da aula e a ausência de cidades repetidas), mutações Swap e por inversão (incluindo uma inversão que desfaz um cruzamento), elitismo, tamanho fixo da população, as duas formas de parada, o tempo medido sem contar o desenho da janela e a reprodutibilidade por seed.
