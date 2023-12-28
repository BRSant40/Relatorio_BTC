import pandas as pd
import yfinance as yf
import matplotlib.pyplot as plt
import numpy as np

pd.options.mode.chained_assignment = None

ativo = 'BTC-USD' # Bitcoin
dados_ativo = yf.download(ativo)

dados_ativo['retornos'] = dados_ativo['Adj Close'].pct_change().dropna()

dados_ativo['retornos_postivos'] = dados_ativo['retornos'].apply(lambda x: x if x > 0 else 0)
dados_ativo['retornos_negativos'] = dados_ativo['retornos'].apply(lambda x: abs(x) if x < 0 else 0)

dados_ativo['media_retornos_positivos'] = dados_ativo['retornos_postivos'].rolling(window = 14).mean()
dados_ativo['media_retornos_negativos'] = dados_ativo['retornos_negativos'].rolling(window = 14).mean()

dados_ativo = dados_ativo.dropna()

dados_ativo['RSI'] = (100 - 100/
                        (1 + dados_ativo['media_retornos_positivos']/dados_ativo['media_retornos_negativos']))

dados_ativo['EMA_8'] = dados_ativo['Close'].ewm(span=56, adjust=False, min_periods=0).mean()

dados_ativo.loc[dados_ativo['Close'] > dados_ativo['EMA_8'], 'compra'] = 'sim' # Se a cotação for maior que a EMA, COMPRA!!
dados_ativo.loc[dados_ativo['RSI'] >= 55, 'compra'] = 'sim' # Se o RSI for maior ou igual a 55, COMPRA!!

dados_ativo.loc[dados_ativo['RSI'] < 55, 'compra'] = 'nao' # Se o RSI for menor que 50, NÃO COMPRA!!
dados_ativo.loc[dados_ativo['Close'] < dados_ativo['EMA_8'], 'compra'] = 'nao' # Se a cotação for menor que o EMA, NÃO COMPRA!!
dados_ativo.loc[dados_ativo['RSI'] > 70, 'compra'] = 'nao' # Se o RSI for maior que 70, NÃO COMPRA!!

ordem_aberta = 0
data_compra = []
data_compra_amanha = []
data_venda = []
data_venda_amanha = []

from datetime import datetime, timedelta

for i in range(len(dados_ativo)):

    if "sim" in dados_ativo['compra'].iloc[i]:
        if ordem_aberta == 0:
            try:
                data_compra.append(
                    dados_ativo.iloc[i + 1].name)  # +1 porque a gente compra no preço de abertura do dia seguinte.
                ordem_aberta = 1
            except:
                data_amanha = datetime.now() + timedelta(days=1)
                data_compra_amanha.append(data_amanha)

    try:

        if dados_ativo['RSI'].iloc[i] < 40 and dados_ativo['Close'].iloc[i] < dados_ativo['EMA_8'].iloc[
            i]:  # Vender se o RSI for menor que 40 e a cotação estiver menor que o EMA
            if ordem_aberta == 1:
                try:
                    data_venda.append(dados_ativo.iloc[i + 1].name)  # vende no dia seguinte q bater 40
                    ordem_aberta = 0
                except:
                    data_amanha = datetime.now() + timedelta(days=1)
                    data_venda_amanha.append(data_amanha)
                    break

    except:
        continue


lucros = dados_ativo.loc[data_venda]['Open'].values/dados_ativo.loc[data_compra]['Open'][:len(data_venda)].values - 1

###################################### INTERFACE INTUITIVA PARA ANALISAR OS RESULTADOS #############################

import tkinter as tk
from tkinter import Scrollbar, Canvas

def on_mousewheel(event):
    canvas.yview_scroll(int(-1*(event.delta/120)), "units")

def on_scrollbar_y(*args):
    canvas.yview(*args)

def on_scrollbar_x(*args):
    canvas.xview(*args)

# Criação da janela principal
janela = tk.Tk()
janela.title("Relatório Diário Bitcoin")

# Configuração do tamanho da janela
largura = 600
altura = 400
largura_tela = janela.winfo_screenwidth()
altura_tela = janela.winfo_screenheight()
x = (largura_tela - largura) // 2
y = (altura_tela - altura) // 2
janela.geometry(f"{largura}x{altura}+{x}+{y}")

# Criar um Canvas
canvas = Canvas(janela, width=largura, height=altura, scrollregion=(0, 0, 1000, 1000))

# Adicionar barras de rolagem vertical e horizontal
scrollbar_y = Scrollbar(janela, orient="vertical", command=on_scrollbar_y)
scrollbar_y.pack(side="right", fill="y")
canvas.configure(yscrollcommand=scrollbar_y.set)

scrollbar_x = Scrollbar(janela, orient="horizontal", command=on_scrollbar_x)
scrollbar_x.pack(side="bottom", fill="x")
canvas.configure(xscrollcommand=scrollbar_x.set)

# Adicionar evento de roda do mouse para rolagem vertical
canvas.bind_all("<MouseWheel>", on_mousewheel)

# Adicionar um grande bloco de texto (simulando muitas informações)
texto_grande = f'''Datas de compra: 
{data_compra[-5:]}\n

Datas de venda: 
{data_venda[-5:]}\n

Ordem de Compra aberta:
{data_compra_amanha}\n

Ordem de Venda aberta:
{data_venda_amanha}
'''
canvas.create_text(10, 10, anchor="nw", text=texto_grande)

# Posicionar o Canvas
canvas.pack(expand=True, fill="both")

# Iniciar o loop principal da interface gráfica
janela.mainloop()
