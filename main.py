import pandas as pd

df = pd.read_excel('Book.xlsx')

# Alinhar resumos

filtro_1 = 'bee |beehive|bees |colonies bee|colony bee'
filtro_2 = 'electronic|arduino|microprocessor|microcontroller|processing video|\
        tiva c|scikit learn|tensor flow|pytorch|machine learning||neural network|\
        humidity sensor|temperature sensor|sound sensor|weight sensor|sensor|\
        image processing|images processing|video processing|videos processing|iot|\
        internet of things|yolo|opencv|neural networks|communication|rfid|\
        artificial intelligence|data acquisition|monitoring system||python|processing image|'\
        'bee detection|bees detection|detecting bee|embedded system'

df_alinhados = df[df['Abstract'].str.contains(filtro_1, case=False)]
df_alinhados = df_alinhados[df_alinhados['Abstract'].str.contains(filtro_2, case=False)]

# Alinhar títulos

df_alinhados = df_alinhados[df_alinhados['TI'].str.contains(filtro_1, case=False)]
df_alinhados = df_alinhados[df_alinhados['TI'].str.contains(filtro_2, case=False)]

# Classificar os resumos: 0 - mal alinhado e 5 - Bem alinhado

classificacao = [5, 4, 3, 2, 1 , 0]
keywords_level_0 = [' ']
keywords_level_1 = ['rfid', 'humidity sensor', 'weight sensor', 'communication', 'temperature sensor', 'sound sensor']
keywords_level_2 = ['electronic', 'iot', 'internet of things','neural network', 'neural networks', 'tensor flow']
keywords_level_3 = ['arduino', 'raspberry', 'tiva c', 'microprocessor', 'microcontroller', 'scikit learn', 'embedded system']
keywords_level_4 = ['video processing', 'images processing', 'videos processing', 'image processing', 'processing image', 'processing video']
keywords_level_5 = ['yolo', 'opencv', 'pytorch', 'artificial itelligence', 'machine learning', 'monitoring system', 'data acquisition',
                    'deep learning']
keywords_lista = [keywords_level_5, keywords_level_4, keywords_level_3, keywords_level_2, keywords_level_1, keywords_level_0]

def condicao_classificacao(x):

    for index, keywords in enumerate(keywords_lista):
        for keyword in keywords:
            if keyword in x:
                return classificacao[index]
        
df_alinhados['AB alinhado'] = df_alinhados['Abstract'].apply(lambda x: condicao_classificacao(x))
df_alinhados['Cit perc.'] = 100*df_alinhados['TC']/df_alinhados['TC'].sum()
df_alinhados.index.name = 'ID'

# Calculando o percentual acumulado de citações para a regra de pareto

soma = 0
for indice, item in zip(df_alinhados.index, df_alinhados['Cit perc.']):
    soma += item
    df_alinhados.loc[indice, '%Acumulada. cit'] = soma
    if soma >= 80:
        df_alinhados.loc[indice, 'Pareto'] = 0
    else:
        df_alinhados.loc[indice, 'Pareto'] = 1

# Se PY >= 2021 => Recente

df_alinhados['Recente'] = df['PY'].apply(lambda x: 1 if x >= 2021 else 0)

# Repescagem de autores

df_autores_renomados = df_alinhados[df_alinhados['Pareto'] == 1]
autores_renomados = []
for autores in df_autores_renomados['AU']:
    autores = autores.split(';')
    for autor in autores:
        if autor not in autores_renomados:
            autores_renomados.append(autor)
    del autores

for index, autores in zip(df_alinhados.index, df_alinhados['AU']):
    autores_lista = autores.split(';')
    for autor in autores_lista:
        if autor in autores_renomados:
            df_alinhados.loc[index, 'Repescagem'] = 1
        else:
            df_alinhados.loc[index, 'Repescagem'] = 0

# Selecionados

df_alinhados['Selecionados'] = df_alinhados['Recente'] + df_alinhados['Pareto'] + df_alinhados['Repescagem']

# Filtro geral

df_alinhados = df_alinhados[(df_alinhados['Selecionados'] >= 1) & (df_alinhados['AB alinhado'] > 0)]
df_alinhados['Pontuação'] = (1.25*df_alinhados['Cit perc.']+0.1)*(3*df_alinhados['Recente'] + 0.95*df_alinhados['AB alinhado'])
df_alinhados = df_alinhados.sort_values(by='Pontuação', ascending=False)

# Dataframe a ser convertido para xlsx

df_alinhados_convertido = df_alinhados[['TI', 'TC', 'PY', 'Pontuação']]
print(len(df_alinhados_convertido))
df_alinhados_convertido.to_excel('artigos_filtrados.xlsx', sheet_name='proknow-c')

# Total: 36 artigos. Base de dados: Web of science