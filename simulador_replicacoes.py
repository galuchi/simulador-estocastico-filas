import math
import numpy as np
import scipy.stats as st

# -----------------------------------------------------------------
# 1. GERADOR DE NÚMEROS ALEATÓRIOS
# -----------------------------------------------------------------
def criar_gerador(semente):
    """
    Cria uma função (closure) que atua como um gerador de 
    números pseudoaleatórios, mantendo seu próprio estado interno (semente).
    """
    x_atual = semente
    A = 16807
    M = 2**31 - 1
    
    def gerar_proximo():
        nonlocal x_atual
        x_atual = (A * x_atual) % M
        return x_atual / M
    
    return gerar_proximo

# -----------------------------------------------------------------
# 2. FUNÇÃO DE SIMULAÇÃO
# -----------------------------------------------------------------
def rodar_uma_replicacao(limite_tempo, semente_inicial):
    """
    Executa uma única rodada (replicação) da simulação.
    Retorna as médias de tempo no sistema, na fila, de serviço
    e ocioso para esta replicação.
    """
    
    gerar_proximo_aleatorio = criar_gerador(semente_inicial)
    
    # Variáveis de estado
    tempo_chegada_relogio_anterior = 0.0
    tempo_fim_servico_anterior = 0.0
    
    # Listas para coletar métricas DESTA replicação
    tempos_no_sistema_cliente = []
    tempos_na_fila_cliente = []
    tempos_de_servico_cliente = []  
    tempos_ociosos_funcionario = [] 

    while True:
        r_tec = gerar_proximo_aleatorio()
        r_ts = gerar_proximo_aleatorio()

        # Calcula o TEC (Exponencial com taxa 0.6)
        tec = -math.log(r_tec) / 0.6
        tempo_chegada_relogio = tempo_chegada_relogio_anterior + tec

        if tempo_chegada_relogio > limite_tempo:
            break

        # Calcula o TS (Exponencial com taxa 0.4 + 0.3)
        ts = -math.log(r_ts) / 0.4 + 0.3
        
        # Métricas da fila
        tempo_inicio_servico = max(tempo_chegada_relogio, tempo_fim_servico_anterior)
        tempo_na_fila = tempo_inicio_servico - tempo_chegada_relogio
        tempo_no_sistema = tempo_na_fila + ts
        tempo_fim_servico = tempo_inicio_servico + ts
        
        # Métrica de ociosidade
        tempo_ocioso = tempo_inicio_servico - tempo_fim_servico_anterior
        
        # Armazena resultados do cliente
        tempos_no_sistema_cliente.append(tempo_no_sistema)
        tempos_na_fila_cliente.append(tempo_na_fila)
        tempos_de_servico_cliente.append(ts)           
        tempos_ociosos_funcionario.append(tempo_ocioso) 

        # Atualiza variáveis para o próximo ciclo
        tempo_chegada_relogio_anterior = tempo_chegada_relogio
        tempo_fim_servico_anterior = tempo_fim_servico

    # Ao final da replicação, calcula as médias para esta rodada
    if not tempos_no_sistema_cliente:
        return 0.0, 0.0, 0.0, 0.0 # Retorna 4 métricas nulas
    
    media_sistema_desta_rodada = sum(tempos_no_sistema_cliente) / len(tempos_no_sistema_cliente)
    media_fila_desta_rodada = sum(tempos_na_fila_cliente) / len(tempos_na_fila_cliente)
    media_servico_desta_rodada = sum(tempos_de_servico_cliente) / len(tempos_de_servico_cliente) 
    media_ocioso_desta_rodada = sum(tempos_ociosos_funcionario) / len(tempos_ociosos_funcionario)
    
    # Este X_i é a média de uma única simulação (agora para 4 métricas)
    return (
        media_sistema_desta_rodada, 
        media_fila_desta_rodada, 
        media_servico_desta_rodada, 
        media_ocioso_desta_rodada
    )

# -----------------------------------------------------------------
# 3. ALGORITMO PRINCIPAL (Estatísticas e Intervalo de Confiança)
# -----------------------------------------------------------------
if __name__ == "__main__":
    
    # Parâmetros da simulação
    N_REPLICACOES = 30     # Número de rodadas (n)
    LIMITE_TEMPO = 60.0    # Duração de cada simulação (minutos)
    CONFIANCA = 0.95       # Nível de confiança (95%)
    
    sementes = [(i * 12345 + 10) for i in range(N_REPLICACOES)]
    
    # Listas para guardar a média de CADA replicação
    resultados_medias_sistema = []
    resultados_medias_fila = []
    resultados_medias_servico = [] 
    resultados_medias_ocioso = []  

    print(f"Executando {N_REPLICACOES} replicações...")
    
    for i in range(N_REPLICACOES):
        semente_atual = sementes[i]
        
        # Desempacota as 4 métricas retornadas
        media_sistema_i, media_fila_i, media_servico_i, media_ocioso_i = \
            rodar_uma_replicacao(LIMITE_TEMPO, semente_atual)
        
        if media_sistema_i > 0: # Ignora rodadas onde nenhum cliente chegou
            resultados_medias_sistema.append(media_sistema_i)
            resultados_medias_fila.append(media_fila_i)
            resultados_medias_servico.append(media_servico_i) 
            resultados_medias_ocioso.append(media_ocioso_i)  
    
    print("Cálculo do Intervalo de Confiança final...")

    # --- Cálculo Estatístico ---
    
    n = len(resultados_medias_sistema) # n efetivo
    if n < 2:
        print("Erro: Não foi possível coletar dados suficientes (n < 2).")
    else:
        # 1. Calcular Média das Médias (x_barra)
        media_geral_sistema = np.mean(resultados_medias_sistema)
        media_geral_fila = np.mean(resultados_medias_fila)
        media_geral_servico = np.mean(resultados_medias_servico) 
        media_geral_ocioso = np.mean(resultados_medias_ocioso)   

        # 2. Calcular Desvio Padrão (s) das médias
        std_dev_sistema = np.std(resultados_medias_sistema, ddof=1)
        std_dev_fila = np.std(resultados_medias_fila, ddof=1)
        std_dev_servico = np.std(resultados_medias_servico, ddof=1)
        std_dev_ocioso = np.std(resultados_medias_ocioso, ddof=1)   

        # 3. Calcular t-crítico (t_{n-1, alpha/2})
        graus_liberdade = n - 1
        alpha = 1 - CONFIANCA
        t_critico = st.t.ppf(1 - alpha / 2, df=graus_liberdade)
        
        # 4. Calcular a meia-largura do intervalo
        meia_largura_sistema = t_critico * (std_dev_sistema / math.sqrt(n))
        meia_largura_fila = t_critico * (std_dev_fila / math.sqrt(n))
        meia_largura_servico = t_critico * (std_dev_servico / math.sqrt(n)) 
        meia_largura_ocioso = t_critico * (std_dev_ocioso / math.sqrt(n))  

        # --- Apresentação dos Resultados ---
        
        print("\n--- RESULTADOS ESTATÍSTICOS FINAIS ---")
        print(f"Baseado em n = {n} replicações válidas.")
        print(f"Nível de Confiança: {CONFIANCA*100:.0f}% | Valor t-crítico: {t_critico:.4f}")
        
        print("\n" + "="*40)
        print(" métrica: TEMPO MÉDIO NO SISTEMA")
        print(f"  Média (x_barra): {media_geral_sistema:.4f}")
        print(f"  Desvio Padrão (s): {std_dev_sistema:.4f}")
        print(f"  Intervalo de Confiança: [{media_geral_sistema - meia_largura_sistema:.4f}, {media_geral_sistema + meia_largura_sistema:.4f}]")

        print("\n" + "="*40)
        print(" métrica: TEMPO MÉDIO DE ESPERA (NA FILA)")
        print(f"  Média (x_barra): {media_geral_fila:.4f}")
        print(f"  Desvio Padrão (s): {std_dev_fila:.4f}")
        print(f"  Intervalo de Confiança: [{media_geral_fila - meia_largura_fila:.4f}, {media_geral_fila + meia_largura_fila:.4f}]")

        print("\n" + "="*40)
        print(" métrica: TEMPO MÉDIO DE SERVIÇO")
        print(f"  Média (x_barra): {media_geral_servico:.4f}")
        print(f"  Desvio Padrão (s): {std_dev_servico:.4f}")
        print(f"  Intervalo de Confiança: [{media_geral_servico - meia_largura_servico:.4f}, {media_geral_servico + meia_largura_servico:.4f}]")

        print("\n" + "="*40)
        print(" métrica: TEMPO MÉDIO OCIOSO (do servidor)")
        print(f"  Média (x_barra): {media_geral_ocioso:.4f}")
        print(f"  Desvio Padrão (s): {std_dev_ocioso:.4f}")
        print(f"  Intervalo de Confiança: [{media_geral_ocioso - meia_largura_ocioso:.4f}, {media_geral_ocioso + meia_largura_ocioso:.4f}]")