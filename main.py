import pandas as pd

df = pd.read_excel('articles2.xlsx')

# Alinhar resumos

filtro_1 = 'bee|bees'
filtro_2 = 'electronic|arduino|microprocessor|microcontroller|processing video|detecting motion|motion detection|\
        scikit learn|tensor flow|pytorch|machine learning||neural network|prediction model|\
        humidity sensor|temperature sensor|sound sensor|weight sensor|audio sensor|predicting model|\
        image processing|images processing|video processing|videos processing|iot|motion detecting|\
        internet of things|yolo|opencv|neural networks|rfid|model prediction|image classification|counting bee\
        artificial intelligence|data acquisition|monitoring|processing image| AI |video processing|'\
        'bee detection|bees detection|detecting bee|embedded system|computer vision|detecion model|processing image|\
        audio detection|detecting audio|audio processing|processing audio|real-time system|real-time monitoring|scikit-learn'

# Alinhar títulos e resumos

df_alinhados = df[df['TI'].str.contains(filtro_1, case=False) & df['TI'].str.contains(filtro_2, case=False)]
df_alinhados = df_alinhados[df_alinhados['Abstract'].str.contains(filtro_1, case=False) & df_alinhados['Abstract'].str.contains(filtro_2, case=False)]

# Classificar os resumos: 0 - mal alinhado e 5 - Bem alinhado

classificacao = [5, 4, 3, 2, 1 , 0]
keywords_level_0 = [' ']
keywords_level_1 = ['rfid', 'humidity sensor', 'weight sensor', 'temperature sensor', 'sound sensor', 'audio sensor', 'predicting model', 
                    'audio processing', 'processing audio', 'detecting audio', 'audio detection', 'prediction', 'python']
keywords_level_2 = ['electronic', 'iot', 'internet of things', 'detection model', 'detecting model']
keywords_level_3 = ['arduino', 'raspberry', 'tiva c', 'microprocessor', 'microcontroller', 'embedded system', 'pil ','neural networks',
                    'real-time system', 'real-time monitoring', 'neural network', ' AI ', 'bee detection', 'bees detection', 'detecting bee']
keywords_level_4 = ['video processing', 'images processing', 'videos processing', 'image processing', 'processing image', 'processing video',
                    'detecting motion', 'motion detecting', 'motion detection']
keywords_level_5 = ['yolo', 'opencv', 'pytorch', 'monitoring system', 'data acquisition', 'deep learning', 'computer vision', 'pillow', 'counting bee',
                    'scikit-learn', 'scikit learn', 'machine learning', 'artificial intelligence', 'image classification', 'tensor flow']
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

# Se PY >= 2020 => Recente

df_alinhados['Recente'] = df['PY'].apply(lambda x: 1 if x >= 2020 else 0)

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
df_alinhados['Pontuação'] = (df_alinhados['Cit perc.'] + 5 + 1.5*df_alinhados['Recente'])*(df_alinhados['AB alinhado'])
df_alinhados = df_alinhados.sort_values(by='Pontuação', ascending=False)

# Dataframe a ser convertido para xlsx

df_alinhados_convertido = df_alinhados[['TI', 'TC', 'PY', 'Pontuação']]
print(len(df_alinhados_convertido))

# Total: 81 artigos. Base de dados: Web of science