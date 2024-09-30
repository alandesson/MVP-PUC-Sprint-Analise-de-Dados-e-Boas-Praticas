# -*- coding: utf-8 -*-
"""MVP PUC - Sprint: Análise de Dados e Boas Práticas.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1pckmR4jOj9sY3OvkAmoz4VQlnD5EMlZ2

# Objetivo:

A Bolsa de Valores Brasileira (B3) negocia ações de empresas de diversos setores da economia tecnologia, mineração, energia e agronegócio. Cada setor tem características próprias e responde de forma diferente a fatores econômicos, como inflação, juros e outros eventos do dia dia brasileiro e mundial. Esses comportamentos fazem com que as ações apresentem variações, que refletem as particularidades de cada setor e a performance das empresas que os compõem.

A análise dos diversos setores da B3 é fundamental para entender como e onde investir. Pois avaliando as acoes e os setores da bolsa podemos entender as dinâmicas de cada setor, como eles reagiram a diferentes cenários econômicos, e ajuda a traçar tendências futuras. Compreender essas movimentações é essencial para investidores, empresas e economistas que buscam antecipar oportunidades e riscos.

Este projeto tem como objetivo investigar o desempenho dos diferentes setores da bolsa nos últimos cinco anos, com foco nas ações que registraram o maior crescimento e rendimento. A partir dessa análise, será possível apresentar de forma clara quais foram as ações e setores mais promissores e suas perspectivas para o futuro.

Em resumo, este projeto prentede fazer uma analise descritiva dos dados coletados para responder às seguintes questões:

1. Como é a distribuição das ações entre os setores?
2. Quais ações tiveram o maior crescimento?
3. Qual setor apresentou o maior e o menor crescimento?
4. Quais ações tiveram o melhor desempenho em cada setor?
5. Qual foi o crescimento dos setores ao longo dos anos?

Em seguida fazer o Pré-processamento de dados e preparar a base para um apredizado supervisionado para prever resultado de ações com base em seus setores e variação de preço.

##Coleta de Dados:

Para obter os dados de valor da ações por dia utilizei a biblioteca do python yfinance, ela é uma biblioteca opensource que utiliza a api de finanças do yahoo para obter seus dados.

A seguir temos um exemplo de como utilizar a biblioteca para extrair os dados do ano de 2023 para ações da Petrobras:
"""

!pip install --upgrade scikit-learn
!pip install investpy

# Configuração para não exibir os warnings
import warnings
warnings.filterwarnings("ignore")

# Importação de pacotes
import pandas as pd
import yfinance as yf
import numpy as np
import missingno as ms # para tratamento de missings
## Transformações Numéricas
from sklearn.preprocessing import MinMaxScaler # para normalização
from sklearn.preprocessing import StandardScaler # para padronização
## Transformações Categóricas
from sklearn.preprocessing import OneHotEncoder
from sklearn.preprocessing import OrdinalEncoder
from sklearn.preprocessing import LabelEncoder

ticker = "PETR4.SA"
start_date = "2023-01-01"
end_date = "2023-12-31"

stock_data = yf.download(ticker, start=start_date, end=end_date)

min_price = stock_data['Low'].min()
avg_price = stock_data['Close'].mean()
max_price = stock_data['High'].max()

total_volume = stock_data['Volume'].sum()

# Print the results
print(f"\nValor mínimo das ações: R${min_price:.2f}")
print(f"Valor final das ações: R${avg_price:.2f}")
print(f"Valor máximo das ações: R${max_price:.2f}")
print(f"Volume total de ações vendidas: {total_volume}")

info = yf.Ticker(ticker)
print(f"Moeda: {info.info['currency']}")
print(stock_data.head())

"""O próximo passo é obter a lista de ações da bolsa de valores brasiliera para que possamos montar e analisar nossa base de dados. No entanto, se você observar no exemplo acima utilizamos o ticker (codigo que representa ação de uma dada empresa). Logo, precisamos de uma forma de obter um conjunto de tickers, para obter esses dados vamos utilizar o pacote investpy. Esse pacote é gratis e sem limitações e é capaz de recuperar dados do Investing.com, que fornece dados de até 39.952 ações, 82.221 fundos, 11.403 ETFs, 2.029 cruzamentos de moedas, 7.797 índices, 688 títulos, 66 commodities, 250 certificados e 4.697 criptomoedas."""

import logging

'''
  Passo opcional para suprimir erros do yfinance, o yfinance ainda não atualizou
sua base de informações de ticker para empresas que entraram na bolsa em 2023

  obs.: os erros gerados não vão impactar o trabalho, pois são empresas novas e
ou delistadas o estudo visa comparar dados de empresas que estão a pelo menos
5 anos na bolsa
'''
logger = logging.getLogger('yfinance')
logger.disabled = True
logger.propagate = False

import investpy
import pandas as pd
import yfinance as yf


# Função para obter todos os tickers da bolsa brasileira (B3)
def getTodosTickersBrasileiros():
    stocks = investpy.stocks.get_stocks(country='brazil')
    tickers = stocks['symbol'].tolist()
    return tickers

def getTickerInfo(ticker):
    stock = yf.Ticker(ticker + ".SA")
    info = stock.info
    # print(info)
    return {
        "nome": info.get("longName", "N/A"),
        "setor": info.get("sector", "N/A"),
        "indústria": info.get("industry", "N/A"),
        "data_entrada_bolsa": info.get("firstTradeDateEpochUtc", "N/A")
    }


# Obtendo a lista de Tickers Brasileiros
tickers = getTodosTickersBrasileiros()

# Obtendo Informações da empresa para cada Ticker
stock_info = []
for ticker in tickers:
    ticker_info = getTickerInfo(ticker)
    if ticker_info:
        stock_info.append({
            "Ticker": ticker,
            "Nome": ticker_info["nome"],
            "Setor": ticker_info["setor"],
            "Indústria": ticker_info["indústria"],
            "Data": ticker_info["data_entrada_bolsa"]
        })

print("Lista de Tickers:")
print(tickers)
print("\nInfo dos 5 primeiros Tickers:")
print(stock_info[:5])

"""Para finalizar a etapa de coleta de dados e concluir a construção da nossa base, de forma que possamos avançar para a descrição, visualização e pré-processamento dos dados, precisamos utilizar o exemplo inicial criado para recuperar os dados de transações financeiras dos tickers, em que obtivemos os dados da Petrobras no período de janeiro a dezembro de 2023."""

def downloadTickerData(ticker, start_date="2019-01-01", end_date="2024-12-31"):
    try:
        stock_data = yf.download(ticker, start=start_date, end=end_date)
        stock_data["Ticker"] = ticker

        return stock_data
    except KeyError:
        print("Ticker Key error!", ticker)
        return None

stock_price = None
for stock in stock_info:
    price_info = downloadTickerData(stock["Ticker"]+".SA")

    if stock_price is None:
      stock_price = price_info
      continue

    if price_info is not None:
        stock_price = pd.concat([stock_price, price_info])

stock_price = stock_price.reset_index()
print(stock_price.head())

"""# Estatísticas descritivas:

Nessa etapa vamos analisar os dados coletados, os dados coletados estão armazenados em duas variaveis ***stock_info*** e ***stock_price***. Vamos começar avaliando o ***stock_info*** seguindo as seguintes questionamentos:

 1. Quantos atributos e instâncias existem?
 2. Quais são os tipos de dados dos atributos?
 3. Há valores faltantes, discrepantes ou inconsistentes?
 4. Para os valores numéricos, qual o mínimo, máximo, mediana, moda, média, desvio-padrão e número de valores ausentes?
"""

import datetime
import pandas as pd

# Número de atributos
num_attributes = len(stock_info[0])

# Número de instâncias
num_instances = len(stock_info)

#convertendo para dataframe
stock_info_df = pd.DataFrame(stock_info)

# Contar valores ausentes
missing_values = stock_info_df.isnull().sum()

# valores inconsistentes
inconsistentes = stock_info_df[stock_info_df['Setor'] == 'N/A']
print(inconsistentes.head())
print(f"\nquantidade de valores inconsistentes {len(inconsistentes['Setor'])} \n")

#removendo valores inconsistentes
stock_info_df = stock_info_df[stock_info_df['Setor'] != 'N/A']

# Único valor número é a Data que e está em epoch time
stock_info_df['Data'] = pd.to_numeric(stock_info_df['Data'], errors='coerce')
# Cálculo do mínimo, máximo, mediana, moda, média e desvio padrão
min_val = stock_info_df['Data'].min()
max_val = stock_info_df['Data'].max()
mode_val = stock_info_df['Data'].mode().iloc[0]  # Obtém a primeira moda
median_val = stock_info_df['Data'].median()
mean_val = stock_info_df['Data'].mean()
std_val = stock_info_df['Data'].std()

# Contar valores ausentes
# missing_values = stock_info_df.isnull().sum()

min_val_date = datetime.datetime.fromtimestamp(min_val).strftime('%d/%m/%Y')
max_val_date = datetime.datetime.fromtimestamp(max_val).strftime('%d/%m/%Y')
median_val_date = datetime.datetime.fromtimestamp(median_val).strftime('%d/%m/%Y')
mode_val_date = datetime.datetime.fromtimestamp(mode_val).strftime('%d/%m/%Y')
mean_val_date = datetime.datetime.fromtimestamp(mean_val).strftime('%d/%m/%Y')
std_val_date = datetime.datetime.fromtimestamp(std_val).strftime('%d/%m/%Y')

print("\n")
print(f"Número de atributos: {num_attributes}")
print(f"Número de instâncias: {num_instances}")
print(f"Impresa mais antiga: {min_val} - {min_val_date}")
print(f"Impresa mais nova  : {max_val} - {max_val_date}")
print(f"Data media: {mean_val} - {mean_val_date}")
print(f"Data maior quantidade de empresas entraram na bolsa: {mode_val} - {mode_val_date}")
print(f"Desvio padrao da entrada de empresas na bolsa: {std_val}")


print(f"\nValores ausentes: {missing_values}")

stock_info_df.head()

"""Ao analisar o ***stock_info*** notamos que ele possui alguns valores inconsistens. Como o objetivo é realizar uma analise por setor, foi necessário remover os elementos cujo setor é desconhecido. Notamos também que que no ***stock_info*** temos: dados de , que entraram na bolsa de 2000 até 2024. Além disso podemos notar que:

1. 749 empresas
2. 257 empresas com dados inconsistens
3. 5 atributos
  - Ticker: String que funciona com ID para empresa
  - Nome: String que representa o nome da Empresa
  - Indústria: String Categorica
  - Setor: String Categorica
  - Data: Numerio representando Data em epoch time

Agora podemos começar avaliar o ***stock_price*** seguindo os mesmos critérios.
"""

stock_price.head()

stock_price = stock_price.reset_index()
print(stock_price.columns)
print(stock_price[stock_price['Date'] == '2019-01-02'])

def calcEstatisticas(df, coluna):
	# Cálculo do mínimo, máximo, mediana, moda, média e desvio padrão
	min_val = df[coluna].min()
	max_val = df[coluna].max()
	median_val = df[coluna].median()
	mode_val = df[coluna].mode().iloc[0]  # Obtém a primeira moda
	mean_val = df[coluna].mean()
	std_val = df[coluna].std()

	# Contar valores ausentes
	missing_values = df[coluna].isnull().sum()

	# Exibir os resultados
	print(f"-- Resultado Coluna {coluna} --")
	print(f"Mínimo: {min_val}")
	print(f"Máximo: {max_val}")
	print(f"Mediana: {median_val}")
	print(f"Moda: {mode_val}")
	print(f"Média: {mean_val}")
	print(f"Desvio Padrão: {std_val}")
	print(f"Número de valores ausentes: {missing_values}\n")

calcEstatisticas(stock_price, "Open")
calcEstatisticas(stock_price, "Close")
calcEstatisticas(stock_price, "Low")
calcEstatisticas(stock_price, "High")
calcEstatisticas(stock_price, "Adj Close")
calcEstatisticas(stock_price, "Volume")

# Número de atributos
num_attributes = len(stock_price.columns)

# Número de instâncias
num_instances = len(stock_price)

print(f"Número de atributos: {num_attributes}")
print(f"Número de instâncias: {num_instances}")

stock_price[stock_price['Adj Close'] == -4791500013568.0]

"""Ao analisar o ***stock_price***, notamos que ele possui alguns valores que parecem inconsistentes, como valores negativos para *Adj Close*. No entanto, isso se deve à forma como é calculado, pois essa conta envolve a dedução de custos de dividendos e desdobramentos de ações. Notamos também que, no ***stock_info***, temos dados de empresas que já estão fora da bolsa, ou seja, precisamos tratar esses dados para remover ações que não estão mais listadas para compra. Em resumo, temos:



1. 800122 registros dividos entre as 913 empresas (cujo 749 possuem dados consistentes em ***stock_info***.
2. 164 empresas com dados inconsistens
3. 8 atributos
  - Date: Data representada no formato *YYYY-MM-DD*
  - Ticker: String que funciona com ID para empresa
  - Open: Campo Numérico que representa o valor da ação no momento da abertura da bolsa
  - High: Campo Numérico que representa o valor máximo da ação no dia
  - Low: Campo Numérico que representa o valor minimo da ação no dia
  - Close: Campo Numérico que representa o valor da ação no momento da fechamento da bolsa
  - Adj Close: Campo Numérico que representa o valor da ação após ajuste do preço.
  - Volume: Campo Numérico que representa a quantidade de ações negociadas.

# Visualizando os Dados:

Nessa etapa vamos criar as primeiras visualizações para facilitar a avaliação dos nossos dados. Primeiramente vamos tentar gerar pespectivas que facilitem a analise do conjundo de dados ***stock_info*** e ***stock_price***.
"""

import matplotlib.pyplot as plt
import seaborn as sns

setor_counts = stock_info_df['Setor'].value_counts()
# Configurando o estilo do Seaborn
sns.set(style="whitegrid")

# Criando o gráfico de pizza
plt.figure(figsize=(8, 6))
plt.pie(setor_counts,
        autopct='%1.1f%%',
        startangle=90,
        pctdistance=0.85,
        textprops={'fontsize': 9})  # Usando a paleta de cores do Seaborn

# Adicionando a legenda
plt.legend(setor_counts.index, title='Setores', loc='upper left', bbox_to_anchor=(0.9, 0.8))

plt.title('Distribuição de Empresas por Setor')
plt.axis('equal')  # Para garantir que o gráfico seja um círculo

plt.show()

"""Analisando o gráfico podemos ver que o maior número de empresas na bolsa são empresas da area de *Consumer Cyclical*, essa area é a area de produtos de consumo como havianas, roupas, toalhas, entre outros."""

stock_info_df[stock_info_df['Setor'] == 'Consumer Cyclical'].head(10)

import pandas as pd

# Convertendo a coluna 'Data' para datetime
stock_price['Date'] = pd.to_datetime(stock_price['Date'])

# Ordenando o DataFrame por Ticker e Data
stock_price_sorted = stock_price.sort_values(by=['Ticker', 'Date'])

# Calculando o preço inicial e final de cada empresa (Ticker)
stock_price_sorted = stock_price_sorted.groupby('Ticker').agg(
    preco_inicio=('Close', 'first'),
    preco_fim=('Close', 'last')
)

# Calculando a variação do preço
stock_price_sorted['Crescimento'] = stock_price_sorted['preco_fim'] - stock_price_sorted['preco_inicio']

# Ordenando as empresas pela variação de preço em ordem decrescente e pegando as top 20
top_20 = stock_price_sorted.sort_values(by='Crescimento', ascending=False).head(20).reset_index()

print(top_20)
# Criando o gráfico
plt.figure(figsize=(10, 6))
plt.bar(top_20['Ticker'], top_20['Crescimento'], color='skyblue')
plt.xlabel('Ticker')
plt.ylabel('Crescimento (%)')
plt.title('Ações que com maior aumento')
plt.xticks(rotation=45)
plt.grid(axis='y')

plt.show()

stock_price_sorted = stock_price_sorted.reset_index()
stock_price_sorted['Ticker'] = stock_price_sorted['Ticker'].str.replace('.SA', '', regex=False)

stock_merged_data = stock_price_sorted.merge(stock_info_df, on='Ticker')

# Calculando o crescimento médio por setor
sector_growth = stock_merged_data.groupby('Setor').agg(sector_change=('Crescimento', 'mean'))

# Setor com maior e menor crescimento
max_growth_sector = sector_growth.idxmax()
min_growth_sector = sector_growth.idxmin()

# print(max_growth_sector)
# print(min_growth_sector)

sector_growth = sector_growth.reset_index()

#Ordenando valores antes de plotar
sector_growth = sector_growth.sort_values(by='sector_change', ascending=False)

# Criando o gráfico de barras com seaborn
plt.figure(figsize=(10, 6))
sns.barplot(x='Setor', y='sector_change', data=sector_growth, hue='Setor', dodge=False, palette='viridis', legend=False)

# Adicionando título e rótulos
plt.title('Crescimento no preço da Ação por Setor')
plt.xlabel('Setor')
plt.ylabel('Crescimento Médio(R$)')
plt.xticks(rotation=90)

# Exibindo o gráfico
plt.show()

stock_merged_data

"""Com o gráfico acima, podemos validar que o setor com maior crescimento médio foi o de tecnologia, impulsionado em grande parte por empresas internacionais listadas na B3, como IBM, Cisco e Oracle, que tiveram grande valorização nos últimos 5 anos.

Outro ponto interessante é que o setor com o pior desempenho foi o de imóveis, algo que pode parecer contraintuitivo, já que muitos investidores consideram fundos imobiliários um investimento seguro. Ao analisar as ações listadas no setor imobiliário, chegamos à seguinte explicação para o resultado observado:

Primeiramente, existem fundos imobiliários com caráter determinado. Esses fundos são criados para arrecadar recursos para a construção de grandes obras e, uma vez que seu objetivo é alcançado e o lucro é distribuído aos seus acionistas, seu valor tende a cair para próximo de zero, impactando negativamente a média das ações do setor. Além disso, muitos fundos imobiliários, especialmente os menores, acabam sendo adquiridos por fundos maiores. Nesse processo, os imóveis mais valiosos geralmente são transferidos para os fundos maiores, enquanto os imóveis que permanecem com os fundos menores tendem a ter menor valor. Isso pode resultar na desvalorização dos fundos menores, impactando o desempenho geral do setor imobiliário.
"""

import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt


stock_merged_data['Valorização'] = stock_merged_data['Crescimento']
stock_merged_data_sorted = stock_merged_data.sort_values(by='Crescimento', ascending=False)

top3_por_setor = stock_merged_data_sorted.groupby('Setor').head(3)
# print(top3_por_setor)

top3_por_setor['Setor'] = pd.Categorical(top3_por_setor['Setor'], categories=top3_por_setor['Setor'].unique(), ordered=True)
df_sorted = top3_por_setor.sort_values(by='Setor')

# Get the unique sectors
sectors = df_sorted['Setor'].unique()

# Create subplots with the number of sectors
fig, axes = plt.subplots(nrows=len(sectors)//3 + 1, ncols=3, figsize=(15, 20))  # Adjust nrows and ncols based on the sector count
axes = axes.flatten()

# Plot each sector in a separate subplot
for i, setor in enumerate(sectors):
    # Filter the data for the current sector
    df_sector = df_sorted[df_sorted['Setor'] == setor]

    # Plot on the corresponding subplot
    sns.barplot(x='Ticker', y='Valorização',hue='Ticker', data=df_sector, ax=axes[i])

    # Set the title to be the sector name
    axes[i].set_title(f'Setor: {setor}')

    # Annotate bars with ticker name and growth value
    for p in axes[i].patches:
        height = p.get_height()
        if height > 0:  # Only annotate positive bars
            axes[i].text(
                p.get_x() + p.get_width() / 2,
                height,
                f'{height:.2f}',
                ha='center',
                va='bottom'
            )

    # Rotate the x-tick labels for better readability
    print(axes[i].get_xticklabels())
    axes[i].set_xticklabels(axes[i].get_xticklabels(), ha='center')

# Remove any empty subplots (if there are fewer sectors than subplots)
for j in range(i+1, len(axes)):
    fig.delaxes(axes[j])

# Adjust layout for readability
plt.tight_layout()
plt.show()

stock_price

import seaborn as sns

stock_merged_data2 = stock_price
stock_merged_data2['Ticker'] = stock_merged_data2['Ticker'].str.replace('.SA', '', regex=False)
stock_merged_data2 = stock_merged_data2.merge(stock_info_df, on='Ticker')

# Agrupar por 'Setor' e 'MonthYear', a criação do MonthYear foi para reduzir o ruido e deixar os graficos mais legiveis
stock_merged_data2['MonthYear'] = stock_merged_data2['Date'].dt.strftime('%m/%y')
sector_growth = stock_merged_data2.groupby(['Setor', 'MonthYear'])['Close'].mean().reset_index()

# Calcular o crescimento percentual ano a ano
sector_growth['Valorização'] = sector_growth.groupby('Setor')['Close'].pct_change() * 100

# Remover valores nulos (pois o primeiro ano de cada setor não terá crescimento)
sector_growth = sector_growth.dropna()

colors = sns.color_palette("tab10", len(sector_growth['Setor'].unique()))
g = sns.FacetGrid(sector_growth, col='Setor', col_wrap=2, height=6, aspect=1.5)

for ax, color, sector in zip(g.axes.flat, colors, sector_growth['Setor'].unique()):
    subset = sector_growth[sector_growth['Setor'] == sector]
    sns.lineplot(x='MonthYear', y='Valorização', data=subset, ax=ax, color=color)
    ax.tick_params(axis='x', labelrotation = 90, labelsize=9)

plt.subplots_adjust(bottom=0.2)
plt.subplots_adjust(top=.95)
g.fig.suptitle('Crescimento dos Setores ao Longo dos Anos (por Setor)', fontsize=16)
plt.show()

"""Após responder as cinco questões propostas e gerar visulizações para melhor compreender nossos dados, podemos avançar para a fase de ajustes e finalização do pré-processamento dos dados.

# Pré-processamento de dados:

Nesse ponto, focaremos nas transformações essenciais na etapa de preparação dos dados, como a conversão de atributos de um tipo para outro, discretização de variáveis contínuas, normalização e padronização dos dados. Essas etapas são fundamentais para melhorar a qualidade e a consistência dos dados, garantindo que estejam prontos para a análise e modelagem subsequentes.
"""

# Para utilizar os dados coletados para treino vamos primeiramente fazer um merge das informação similarmente ao que foi feito durante algumas etapas da visualização dos dados. Formando uma base de dados unica.
stock_data = stock_price
stock_data['Ticker'] = stock_data['Ticker'].str.replace('.SA', '', regex=False)
stock_data = stock_data.merge(stock_info_df, on='Ticker')
stock_data = stock_data.reset_index()

stock_data

"""Primeiramente vamos começar removendo as colunas level_0 e index que foram introduzidas durante o processo de formação da base. Visto que esses indexes não tem relevancia para nossa base e futuro treinamento. Além delas, vamos remover a coluna Nome, pois acreito que não tem um valor siginificativo para o treinamento de um modelo que deseja prever o variação de ações com base em seu setores."""

stock_data = stock_data.drop(['level_0', 'index', "Nome"], axis=1)
stock_data.columns

"""Em seguida vamos remover possiveis registros repetidos"""

stock_data.drop_duplicates(inplace=True)
stock_data.dropna(inplace=True)

"""Próximo passo é converter e renomear as colunas Date e Data para datetime e renomea-las para facilitar a compreenção dos seu significado."""

stock_data["Data Entrada B3"] = pd.to_datetime(stock_data["Data"], unit='s')
stock_data["Data Negociacao B3"] = pd.to_datetime(stock_data["Date"])

stock_data = stock_data.drop(['Data', 'Date'], axis=1)

stock_data

"""Agora vamos garantir que os valores de Open,	High, Low, Close Adj, Close,	Volume são númericos"""

stock_data['Open'] = pd.to_numeric(stock_data['Open'])
stock_data['High'] = pd.to_numeric(stock_data['High'])
stock_data['Low'] = pd.to_numeric(stock_data['Low'])
stock_data['Adj Close'] = pd.to_numeric(stock_data['Adj Close'], errors='coerce')
stock_data['Close'] = pd.to_numeric(stock_data['Close'])
stock_data['Volume'] = pd.to_numeric(stock_data['Volume'])

stock_data.head()

"""Agora vamos introduzir uma coluna nova relevante para o treinamento do modelo supervisionado, uma coluna chamada resultado que representará se devemos ou não ter comprado a ação naquele dia."""

stock_data = stock_data.sort_values(by=['Ticker', 'Data Negociacao B3'])

# Step 2: Group by 'Ticker' and shift the 'Close' column by -1 within each group
stock_data['Tomorrow_Close'] = stock_data['Adj Close'].shift(-1)

# Step 3: Create the 'resultado' column (1 if tomorrow's Close is greater than today's, 0 otherwise)
stock_data['resultado'] = (stock_data['Tomorrow_Close'] > stock_data['Close']).astype(int)

# Step 4: Drop the 'Tomorrow_Close' column (optional)
stock_data = stock_data.drop(columns=['Tomorrow_Close'])

# print(stock_data[(stock_data['Ticker'] == 'AALL34') & (stock_data['Data Negociacao B3'] == '2019-10-09')])
# print(stock_data[(stock_data['Ticker'] == 'AALL34') & (stock_data['Data Negociacao B3'] == '2019-10-08')])

"""Próxima etapa é normailizar nossos valores númericos, como um dos nosso objetivos é treinar um modelo para fazer predições, a normalização pode levar a uma convergência mais rápida durante o treinamento, principalmente para algoritmos baseados em gradiente descendente, como regressão linear e redes neurais."""

scaler = MinMaxScaler()
stock_data[['Open', 'High', 'Low', 'Adj Close', 'Close', 'Volume']] = scaler.fit_transform(stock_data[['Open', 'High', 'Low', 'Adj Close', 'Close', 'Volume']])

stock_data.head()

"""Proximo passo é aplicar OneHotEncoding nas nossas variaveis categoricas Setor,
Indústria e Ticker. No entanto Indústria e Tickers possuem muitas categorias, o que estourou o limite de memoria do colabs. Logo para este caso vamos aplicar um label encoder para a coluna de indústria.
"""

label_encoder = LabelEncoder()
stock_data['Indústria'] = label_encoder.fit_transform(stock_data['Indústria'])

# num_sectors = stock_data['Setor'].nunique()
# num_industries = stock_data['Indústria'].nunique()
# num_ticker = stock_data['Ticker'].nunique()

# print(f'Number of unique sectors: {num_ticker}')
# print(f'Number of unique sectors: {num_sectors}')
# print(f'Number of unique industries: {num_industries}')
# print(len(stock_data))

# Step 2: Apply One-Hot Encoding
encoder = OneHotEncoder(sparse_output=False)
encoded_features = encoder.fit_transform(stock_data[['Ticker', 'Setor']])

# Create a DataFrame for the One-Hot Encoded features
encoded_df = pd.DataFrame(encoded_features, columns=encoder.get_feature_names_out(['Ticker', 'Setor']))

# Combine the original DataFrame with the encoded features
final_df = pd.concat([stock_data, encoded_df], axis=1)

final_df.head()

final_df = final_df.drop(['Ticker', 'Setor'], axis=1)
final_df.head()

"""Agora, nosso conjunto de dados foi completamente processado e podemos utilizar o DataFrame ***final_df*** para treinar um modelo de previsão, tendo a coluna Resultado como a variável alvo (saída esperada). E assim, o modelo poderá decidir se devemos ou não adquirir a ação, indicando se o preço tende a subir ou não."""