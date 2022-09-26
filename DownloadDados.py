import MetaTrader5 as mt5
import pandas as pd
from datetime import datetime, timedelta
import pytz
import numpy as np

from bs import *
##TODO: Puxar automático a bibliotecas BS

class DownloadVolHist:
    def __init__(self, ativo, num_dias_vol, num_dias_intervalo, num_dias_media):

        mt5.initialize()

        self.dados = pd.DataFrame(columns=['Dia', 'Volatilidade', 'Media'])
        self.num_dias = num_dias_intervalo

        lista_dados = mt5.copy_rates_from_pos(ativo, mt5.TIMEFRAME_D1, 0, num_dias_vol + num_dias_media + num_dias_intervalo - 1)

        #calcula a volatilidade histórica do ativo
        retornos = []
        dia = []
        for idx, v in enumerate(lista_dados):
            if idx != 0:
                retornos.append(np.log(v['close'] / lista_dados[idx - 1]['close']))
                dia.append(v['time'])     
 
        sigma = []
        dia_sigma = []
        for idx, r in enumerate(retornos):
            if idx <  num_dias_intervalo + num_dias_media - 1:
                sigma.append(np.sqrt(252) * np.std(retornos[idx:idx+num_dias_vol]))
                dia_sigma.append(dia[idx+num_dias_vol-1])       
        

        for idx, s in enumerate(sigma):
            if idx < num_dias_intervalo:
                self.dados = self.dados.append(
                    {"Dia": datetime.utcfromtimestamp(dia_sigma[idx+num_dias_media-1]).strftime('%d/%m/%Y'), 
                    "Volatilidade": sigma[idx+num_dias_media-1], 
                    "Media": np.mean(sigma[idx:idx+num_dias_media])},
                    ignore_index=True)
      
        
        mt5.shutdown()
            

    def get_volHistorica(self):
        return self.dados

class DownloadVolImp:
    def __init__(self, ativo, num_dias_vol, juros):

        self.hoje = datetime.today()

        mt5.initialize()

        lista_opcoes_suja = mt5.symbols_get(ativo[0:4])

        vencimentos = []

        for l in lista_opcoes_suja:
            if l.expiration_time > self.hoje.timestamp():
                exist = 0
                for v in vencimentos:
                    if v == l.expiration_time:
                        exist = 1
                if exist == 0:
                    vencimentos.append(l.expiration_time)
        vencimentos.sort()

        self.lista_call = pd.DataFrame(columns=['Codigo', 'Strike'])
        self.lista_put = pd.DataFrame(columns=['Codigo', 'Strike'])

        data_vencimento = vencimentos[0]#Pega apenas as opções deste vencimento

        for o in lista_opcoes_suja:
            if o.expiration_time == data_vencimento:
                if o.option_right == 0:
                    self.lista_call = self.lista_call.append(
                    {"Codigo": o.name, 
                    "Strike": o.option_strike},
                            ignore_index=True)
                        
                else:
                    self.lista_put = self.lista_put.append(
                    {"Codigo": o.name, 
                    "Strike": o.option_strike},
                            ignore_index=True)

        self.lista_call.sort_values(by='Strike', ascending=True)
        self.lista_put.sort_values(by='Strike', ascending=True)

        ############################################################
        ####### Calculo da Lista de Volatilidade Implicita
      
        lista_valores_acao = mt5.copy_rates_from_pos(ativo, mt5.TIMEFRAME_D1, 0, num_dias_vol)

        self.dados = pd.DataFrame(columns=['Dia', 'Vol Call', 'Vol Put'])

        for idx, a in enumerate(lista_valores_acao):
            existe_call = 0
            existe_put = 0
            ########################################
            ## Dados CALL
            idx_opcao = self.call_otm(a['close'])
            if idx_opcao != -1:     
                codigo_opcao = self.lista_call["Codigo"][idx_opcao]
                dados_opcao = mt5.copy_rates_from(codigo_opcao, mt5.TIMEFRAME_D1, datetime.utcfromtimestamp(a["time"]), 1)
                if (dados_opcao):
                    data_op = datetime.utcfromtimestamp(dados_opcao[0]["time"])
                    
                    if (data_op == datetime.utcfromtimestamp(a["time"])):
                        dias = np.busday_count(data_op.strftime('%Y-%m-%d'), datetime.utcfromtimestamp(data_vencimento).strftime('%Y-%m-%d'))                    
                        vi_call = bs().call_implied_volatility(dados_opcao[0]['close'], a['close'], self.lista_call["Strike"][idx_opcao], dias/252, juros)
                        existe_call = 1

                        print("----------- CALL -------------------------")
                        d = data_op.strftime('%d/%m/%Y')
                        print(f'Data opção: {d}') 
                        d = datetime.utcfromtimestamp(a["time"]).strftime('%d/%m/%Y')
                        print(f'Data da ação: {d}')

                    else:
                        print(f'ALERTA: Problema na sincronização de datas da opção {codigo_opcao} com a ação!')
                        d = data_op.strftime('%d/%m/%Y')
                        print(f'Data opção: {d}') 
                        d = datetime.utcfromtimestamp(a["time"]).strftime('%d/%m/%Y')
                        print(f'Data da ação: {d}')

                else:
                    print(f'ALERTA: Falha na leitura da opção {codigo_opcao}')
            else:
                print(f'ALERTA: Problema na identificação da CALL ATM!')

            #########################################
            ## Dados PUT
            idx_opcao = self.put_otm(a['close'])
            if idx_opcao != -1:     
                codigo_opcao = self.lista_put["Codigo"][idx_opcao]
                dados_opcao = mt5.copy_rates_from(codigo_opcao, mt5.TIMEFRAME_D1, datetime.utcfromtimestamp(a["time"]), 1)
                if (dados_opcao):
                    data_op = datetime.utcfromtimestamp(dados_opcao[0]["time"])
                    
                    if (data_op == datetime.utcfromtimestamp(a["time"])):
                        dias = np.busday_count(data_op.strftime('%Y-%m-%d'), datetime.utcfromtimestamp(data_vencimento).strftime('%Y-%m-%d'))                    
                        vi_put = bs().call_implied_volatility(dados_opcao[0]['close'], a['close'], self.lista_put["Strike"][idx_opcao], dias/252, juros)
                        existe_put = 1

                        print("----------- PUT -------------------------")
                        d = data_op.strftime('%d/%m/%Y')
                        print(f'Data opção: {d}') 
                        d = datetime.utcfromtimestamp(a["time"]).strftime('%d/%m/%Y')
                        print(f'Data da ação: {d}')

                    else:
                        print(f'ALERTA: Problema na sincronização de datas da opção {codigo_opcao} com a ação!')   
                        d = data_op.strftime('%d/%m/%Y')
                        print(f'Data opção: {d}') 
                        d = datetime.utcfromtimestamp(a["time"]).strftime('%d/%m/%Y')
                        print(f'Data da ação: {d}')

                else:
                    print(f'ALERTA: Falha na leitura da opção {codigo_opcao}')
            else:
                print(f'ALERTA: Problema na identificação da CALL ATM!')

            #############################################
            ## Salvar os dados

            if ((existe_call == 1) and (existe_put == 1)):

                self.dados = self.dados.append(
                        {"Dia": data_op.strftime('%d/%m/%Y'),
                        "Vol Call": vi_call,
                        "Vol Put": vi_put},
                                ignore_index=True)
          
        mt5.shutdown()

    def get_volImplicita(self):
        return self.dados

    def call_otm(self, valor):
        menor_diferenca = 2
        idx_atm = -1
        for idx in self.lista_call.index:
            if (abs(self.lista_call['Strike'][idx] - valor) < menor_diferenca):
                menor_diferenca = abs(self.lista_call['Strike'][idx] - valor)
                idx_atm = idx
        return idx_atm

    def put_otm(self, valor):
        menor_diferenca = 2
        idx_atm = -1
        for idx in self.lista_put.index:
            if (abs(self.lista_put['Strike'][idx] - valor) < menor_diferenca):
                menor_diferenca = abs(self.lista_put['Strike'][idx] - valor)
                idx_atm = idx
        return idx_atm





        




        

        
