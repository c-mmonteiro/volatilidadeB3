import MetaTrader5 as mt5
import pandas as pd
from datetime import datetime, timedelta
import pytz
import numpy as np

class DownloadDados:
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
                sigma.append(np.sqrt(252) * np.std(retornos[idx:idx+num_dias_vol])*100)
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




        

        
