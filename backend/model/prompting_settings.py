from services.history import get_chat_history

def create_prompt(context, user_query, max_output_tokens=2048, temperature=0.2, top_p=0.9, top_k=30):
    prompt = f"""
    Contexto: {context}

    Pergunta: {user_query}

    Histórico: {get_chat_history()}

    Para responder, organize as informações em tópicos sempre, descreva de maneira direta e fluida a experiência geral dos usuários com o produto, mencionando os pontos positivos e negativos de forma integrada, sem listas ou formatação rígida. Finalize com uma breve recomendação, caso aplicável.
    """

    return prompt, temperature, max_output_tokens, top_k, top_p

#Contexto: 

#Temperature: afeta diretamente a diversidade e a criatividade das respostas geradas.

#  Baixa Temperatura (por exemplo, 0.1 a 0.4):
#   Respostas Coerentes: Gera respostas mais previsíveis e conservadoras, pois o modelo tende a escolher palavras com altas probabilidades.
#   Menor Criatividade: Pode resultar em respostas repetitivas ou genéricas, com pouca variação na linguagem.
#   Uso Ideal: Útil quando se busca precisão e clareza, como em respostas factuais ou técnicas.

#  Temperatura Média (por exemplo, 0.5 a 0.7):
#   Equilíbrio entre Coerência e Criatividade: Oferece um bom compromisso entre respostas seguras e criativas.
#   Variação Moderada: Permite uma diversidade razoável nas respostas, mantendo alguma consistência.

#  Alta Temperatura (por exemplo, 0.8 a 1.0 ou mais):
#   Respostas Criativas: Gera respostas mais variadas e inesperadas, pois o modelo é incentivado a explorar palavras menos prováveis.
#   Maior Risco de Incoerência: Pode resultar em respostas que fogem do contexto ou que são menos coerentes.
#   Uso Ideal: Útil para situações que requerem originalidade ou criatividade, como em histórias, poesia ou brainstorming.

#Top_p: amostra palavras com base em uma soma cumulativa de probabilidade. Em vez de selecionar um número fixo de palavras (k),
#  ele considera as palavras cuja soma das probabilidades cumulativas atinge um determinado limiar p. As palavras são ordenadas por 
# probabilidade, e o modelo inclui palavras até que a soma de suas probabilidades atinja o valor p. Por exemplo, se p = 0.9, o modelo 
# irá considerar as palavras que, juntas, representem 90% da probabilidade total.
# Exemplo: Um valor baixo de p (por exemplo, 0.2) resulta em um conjunto de palavras muito restrito, semelhante ao top_k, e produz 
# respostas mais conservadoras.Um valor mais alto (por exemplo, 0.9) permite uma maior diversidade nas respostas, pois pode incluir 
# palavras menos prováveis, resultando em respostas mais variadas e potencialmente mais criativas.

#Top_k: Limita a amostragem às k palavras mais prováveis na distribuição de probabilidade 
# gerada pelo modelo.Quando o modelo gera a próxima palavra, ele considera apenas as k palavras com as maiores probabilidades. 
# As demais palavras (as de menor probabilidade) são descartadas da amostragem.
# Exemplo: Um valor baixo de k (por exemplo, 5) resulta em respostas mais conservadoras 
# e focadas, pois limita as opções a palavras muito prováveis.
# Um valor mais alto (por exemplo, 50 ou 100) pode levar a respostas mais variadas e criativas, mas também pode aumentar o risco de 
# incoerências.

