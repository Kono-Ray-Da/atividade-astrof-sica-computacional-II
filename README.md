  Essa atividade tem como objetivo analisar eventos de raios cósmicos e suas características, bem como analisar sinais de antenas do Observatório Pierre Auger. 
Para as análises, foram construídos dois códigos em C++ separados que estão na pasta "src": "Projeto.cc", com as análises dos raios cósmicos; "AntenasAug.cc" para a análise das antenas. No código "Projeto.cc", usamos os dados de "Eventos.txt" e "2MASS.txt" (pasta "dados" -> "DadosRaiosCosmicos"), com informações sobre os eventos e fontes de galáxias, respectivamente. "AntenasAug.cc": utilizamos dados de posição ("position.txt") e espectro dos dois canais de cada antena ("Files_Spectrograma"), ambos na pasta "dados"->"DadosAug".
Entre as análises desenvolvidas, destacam-se:
  * Análise da distribuição espacial de eventos de raios cósmicos de ultra-alta energia (UHECR).
  * Investigação da possível associação angular entre eventos de UHECR e fontes astrofísicas, com ênfase em galáxias starburst.
  * Estudo da relação entre energia dos eventos e distância das fontes.
  * Processamento e análise de dados de antenas.
  * Comparação dos canais de observação e análise de seus perfis temporais e espectrais.

  Os arquivos resultantes dessas análises se encontram na pasta "resultados" e foram usados de base para a construção dos códigos em Python (pasta "python") que geraram gráficos e mapas que foram armazenados na pasta "Figuras" 
