# Simulador Estocástico de Filas (Método das Replicações)

Este projeto implementa um simulador de eventos discretos para um sistema de filas com um único servidor (single-server queue). O objetivo é analisar o desempenho do sistema utilizando o método estatístico das Múltiplas Replicações Independentes.

O simulador foi desenvolvido em Python como parte da disciplina de Modelagem e Avaliação de Desempenho de Sistemas Computacionais

## Funcionalidades
* **Simulação de Eventos:** Gera chegadas de clientes (TEC) e tempos de serviço (TS) baseados em distribuições probabilísticas.

* **Múltiplas Replicações:** Executa 30 rodadas independentes (com sementes aleatórias distintas) para garantir validade estatística.

* **Cálculo de Métricas:** Coleta dados sobre:

  * Tempo médio no sistema.

  * Tempo médio de espera na fila.

  * Tempo médio de serviço.

  * Tempo médio ocioso do servidor.

* **Análise Estatística:** Calcula a média geral, desvio padrão e o Intervalo de Confiança de 95% (usando a distribuição t-Student) para todas as métricas.

## Saída Esperada

O programa exibirá no console o progresso das replicações e, ao final, um relatório estatístico contendo:
* Número de replicações válidas utilizadas ($n$).
* O valor $t$-crítico utilizado.
* Para cada métrica (Sistema, Fila, Serviço, Ociosidade):
  * Média das médias ($\bar{x}$).
  * Desvio padrão ($s$).
  * Intervalo de Confiança calculado (Min, Max).

