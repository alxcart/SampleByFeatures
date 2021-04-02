# functions e constants plugins
# executable in Terminal Python QGIS 
from qgis.core import *
# #### Importar biblioteca "random"
from PyQt5.QtWidgets import QAction, QFileDialog, QMessageBox
from qgis.core import *
from qgis.PyQt.QtCore import *
import os.path 
from qgis.utils import *
import random
from osgeo import ogr
from .constants import * # constants of project

"""
# Sampling plan / Plano de amostragem
#Inspection level / Nivel_de_Inspecao = self.dlg.comboBoxLevel.currentIndex()
#dicSampleLength={2:[2,2,3],9:[2,3,5],16:[3,5,8],26:[5,8,13],51:[5,13,20],91:[8,20,32],151:[13,32,50],281:[20,50,80],501:[32,80,125],1201:[50,125,200],3201:[80,200,315],10001:[125,315,500],35001:[200,500,800],150001:[315,800,1250],500001:[500,1250,2000]}
# coding: utf-8
# # Plano de amostragem
# ## Objetivo
# Permitir a elaboração do plano de amostragem simples, dupla ou múltipla para a realização das inspeções de qualidade, por orientada por feição ou por área, em ambiente QGIS. 
# ### ESCOPO
# - 1o letra código: depende do tamanho da população (N) e do nível de inspeção (I, II ou III)
# - 2o tamanho da amostra (n): 
#     - depende do tamanho da população (N)
#     - depende do LQA
#         - 1 a 10%
#     - depende do do tipo de inspeção
#         - simples
#         - dupla
#         - múltipla
# - LQA: variável selecionada pelo usuário
# - resultado = tamanho da amostra (n)
# - informar o plano de amostragem escolhido.   
#### Tratar exceções
# Quando o tamanho da população for igual a 0 ou 1
# - N_min: min_1 [1,0,0]
# - N_zero: min_1 [1,0,0]
# - N_big: max_S [800, 1250, 3150] (#acima de 500001)
# ### FORA ESCOPO
# - número de aceitação (Ac) para planos dupla e múltipla
# - número de rejeição (Re)
# - desejável Ac e Re dos planos de amostragem: simples, dupla e múltipla
# - informa o Ac segundo o plano de amostragem simples para classificação do LQA. 
# ## DESENVOLVIMENTO (Python)
# #### Constantes do plugin
# ##### Tabela 1 - Letra código com base no tamanho da populacao (N)
"""
dicSampleLength={2:[2,2,3],
                 9:[2,3,5],
                 16:[3,5,8],
                 26:[5,8,13],
                 51:[5,13,20],
                 91:[8,20,32],
                 151:[13,32,50],
                 281:[20,50,80],
                 501:[32,80,125],
                 1201:[50,125,200],
                 3201:[80,200,315],
                 10001:[125,315,500],
                 35001:[200,500,800],
                 150001:[315,800,1250],
                 500001:[500,1250,2000]}

"""
# ##### Tabela 2 - Plano de amostragem simples, dupla e múltipla
# De acordo com o LQA desejado o tamanho da amostra (n), obtido com base no tamanho da população (N), poderá ser confirmado ou sofrer um ajuste (para cima ou para baixo). 
# Dicionário onde a chave é o tamanho da amostra (n)
# - key - tamanho da amostra (n) obtido na Tabela 1
# - "letra código" - posição (0)
# - tipo inspeção
# -- simples (1)
# -- dupla (2)
# -- múltipla (3)
# - Limite de Qualidade Aceitável (LQA) (10 posições)
#     -- 0,40% (4)
#     -- 0,65% (5)
#     -- 1,00% (6)
#     -- 1,50% (7)
#     -- 2,50% (8)
#     -- 4,00% (9)
#     -- 6,50% (10)
#     -- 10,00% (11)
#     -- 15,00% (12)
#     -- 25,00% (13)
"""
List_LQA = ["0,40%", "0,65%", "1,00%", "1,50%", "2,50%", "4,00%", "6,50%", "10,00%", "15,00%","25,00"]
List_nivel_inspecao = ["I", "II", "III"]
List_tipo_inspecao = ["simples", "dupla", "múltipla"]


TAB_LQA = {2:["A", 2,0,0,"down","down","down","down","down","down",0,"down","down",1], 
                3:["B", 3,2,0,"down","down","down","down","down",0,"up","down",1,2], 
                5:["C", 5,3,0,"down","down","down","down",0,"up","down",1,2,3], 
                8:["D", 8,5,2,"down","down","down",0,"up","down",1,2,3,5], 
                13:["E", 13,8,3,"down","down",0,"up","down",1,2,3,5,7], 
                20:["F", 20,13,5,"down",0,"up","down",1,2,3,5,7,10], 
                32:["G", 32,20,8,0,"up","down",1,2,3,5,7,10,14], 
                50:["H", 50,32,13,"up","down",1,2,3,5,7,10,14,21], 
                80:["J", 80,50,20,"down",1,2,3,5,7,10,14,21,"up"], 
                125:["K", 125,80,32,1,2,3,5,7,10,14,21,"up","up"], 
                200:["L", 200,125,50,2,3,5,7,10,14,21,"up","up","up"], 
                315:["M", 315,200,80,3,5,7,10,14,21,"up","up","up","up"], 
                500:["N", 500,315,125,5,7,10,14,21,"up","up","up","up","up"], 
                800:["P", 800,500,200,7,10,14,21,"up","up","up","up","up","up"], 
                1250:["Q", 1250,800,315,10,14,21,"up","up","up","up","up","up","up"], 
                2000:["R", 2000,1250,500,14,21,"up","up","up","up","up","up","up","up"]}

# ### Função tamanho da amostra (n)
# Funcao para encontrar a letra codigo a partir do N e do nivel de inspecao
def n0(N, nivel_inspecao): #função sample size inicial
    """ Tamanho da amostra (n): esta função retorna o tamanho da amostra (n), a partir do tamanho da população (N) e do
    nivel de inspeção: 0 - brando; 1 - normal; 2 - severo. 
    Se N = 1 será inspeção completa.
    Se N < 1 não haverá inspeção. 
    Se N >=2 inspecao amostral
    O resultado contempla: o tamanho da amostra inicial"""
    # Identificando a chave do tamanho da amostra
    if N==1:
        msg = "inspeção completa"
        letra_codigo = "inspeção completa"
        sample_size = 1
    if N < 1:
        msg = "camada sem registro"
        letra_codigo = "camada sem registro"
        sample_size = 0
    if N>=2:
        msg = "inspeção amostral"
        for i in sorted(dicSampleLength.keys(),reverse=True):
            if N >= i:
                index1 = i
                break
        # tamanho da amostra inicial n0, sem considerar o LQA desejado. 
        sample_size=dicSampleLength[index1][nivel_inspecao]
        letra_codigo = TAB_LQA.get(sample_size)[0]

    return sample_size, msg , letra_codigo
    #tamanho da amostra, mensagem, letra codigo

# ### Função: número de aceitação (Ac) a partir de n e do LQA
def Ac(n, lqa):
    """
    Esta função retorno o número de aceitação (Ac) 
    com base no tamanho da amostra (n) e 
    no limite de qualidade aceitável  (LQA)
    """
    if n>=2 and n<=2000:
        num_aceitacao = TAB_LQA.get(n)[lqa] 
        letra_codigo = TAB_LQA.get(n)[0]
    if n <= 0:
        num_aceitacao = 0
        letra_codigo = "sem letra código"
    if n == 1:
        num_aceitacao = 1
        letra_codigo = "sem letra código"
    if n>2000:
        n=2000
        num_aceitacao = TAB_LQA.get(n)[lqa]
        letra_codigo = TAB_LQA.get(n)[0]
    
    if num_aceitacao == "down":
        tab_index = {}
        letra_codigo = TAB_LQA.get(n)[0]
        for i in enumerate (TAB_LQA):
            #print (i[0], i[1], TAB_LQA.get(i[1])[lqa])
            tab_index[i[0]]=i[1], TAB_LQA.get(i[1])[lqa], TAB_LQA.get(i[1])[0]
            for j in tab_index:
                if tab_index[j][0]==n and tab_index[j][1]=="down":          
                    x = j + 1
                    if tab_index.get(x) is not None:
                        n, num_aceitacao, letra_codigo = tab_index.get(x)
                        #print (n)
                        #print (Ac)
    if num_aceitacao == "up":
        tab_index = {}
        letra_codigo = TAB_LQA.get(n)[0]
        #Ac = Ac(n, lqa)
        for i in enumerate (sorted((TAB_LQA),reverse=True)):
            #print (i[0], i[1],  TAB_LQA.get(i[1])[lqa])
            tab_index[i[0]]=i[1], TAB_LQA.get(i[1])[lqa], TAB_LQA.get(i[1])[0]
            for j in tab_index:
                if tab_index[j][0]==n and tab_index[j][1]=="up":          
                    x = j + 1
                    if tab_index.get(x) is not None:
                        n, num_aceitacao, letra_codigo = tab_index.get(x)
                        #print (n)
                        #print (Ac)
    return n, num_aceitacao, letra_codigo

"""
# #### Função: seleciona plano de amostragem 
### Função: tipo de inspeção (simples, dupla ou múltipla)
# - simples (0) 1
# - dupla (1) 2 
# - múltipla (2) 3
###### Nota: o plano de amostragem dupla começa em 3 e o 
plano de amostragem múltipla começa no 8. Para n=2; n=3 e n=5 
existe especificidades. 
"""
def n_final(n, tipo_inspecao):
    if tipo_inspecao==0:
        ns = TAB_LQA[n][1]
        msg = "inspeção amostral simples"
        n = ns
    if tipo_inspecao==1:
        nd = TAB_LQA[n][2]
        msg = "inspeção amostral dupla"
        if nd==0:
            nd = TAB_LQA[n][1]
            msg = "inspeção amostral simples"
        n = nd
    if tipo_inspecao==2:
        nm = TAB_LQA[n][3]
        msg = "inspeção amostral múltipla"
        if nm==0:
            nm = TAB_LQA[n][2]
            msg = "inspeção amostral dupla"
            if nm==0:
                nm = TAB_LQA[n][1]
                msg = "inspeção amostral simples"
        n = nm
       
    nfinal = n
    return nfinal, msg

# ### Função: Seleciona amostra 

def select_sample (N, n):
    #n = sample_plan(N)[0]
    randomNum = random.sample(range(N),1)[0]
    isSelectedId = random.sample(range(N), n)

    return randomNum, isSelectedId

"""
# ### Função: Plano de amostragem
# #### Teste local
# - População 
# - Nível de inspeção (0 a 2) 
# - Tipo de Inspeção  (0 a 2)
# - Limite de Qualidade Aceitável (LQA) (10 posições)
#     -- 0,40% (4)
#     -- 0,65% (5)
#     -- 1,00% (6)
#     -- 1,50% (7)
#     -- 2,50% (8)
#     -- 4,00% (9)
#     -- 6,50% (10)
#     -- 10,00% (11)
#     -- 15,00% (12)
#     -- 25,00% (13)
"""

### main fuction - Elaboracao Plano de Amostragem
def sample_plan (N, nivel_inspecao = 1, lqa = 9, tipo_inspecao = 0):
    """ plano de amostragem : esta função retorna o tamanho da amostra (n), a partir do tamanho da população (N), 
    do nivel de inspeção e do limite de qualidade aceitável (LQA) desejado. 
    O resultado contempla: 
    - uma lista com a identificação das amostras selecionadas de forma aleatória, 
    - o tamanho da amostra, 
    - a letra-codigo final, e
    - número aleatório sorteado """

    if N>=2:
        n, msg, letra_codigo_i = n0(N, nivel_inspecao)
        n, num_aceitacao, letra_codigo_f = Ac(n, lqa) #Ac = num_aceitacao
        if n>=2:
            n, msg = n_final(n, tipo_inspecao)
        if N<=n:
            msg = "inspecao completa"
    if N==1: # and n==1:
        msg = "inspeção completa"
        num_aceitacao = 1
        n = 1
        letra_codigo_i = ""
        letra_codigo_f = ""        
    if N <= 0: # and n==0:
        msg = "camada sem registro"
        num_aceitacao = 0
        n = 0
        letra_codigo_i = ""
        letra_codigo_f = ""
    return N, n, num_aceitacao, letra_codigo_i, letra_codigo_f, msg

##### Funcoes da implementacao - ligacao com a UI 
def preview_n(self):
    """ #Returns the sample size preview to select layer / Retorna a pré-visualização do tamanho da amostra da camada selecionada. 
    #Input data selection"""
    index = self.dlg.comboBox.currentIndex()
    selection = self.dlg.comboBox.itemData(index)

# Executa apenas se houver uma seleção no comboBox
    if selection is not None:
        features = QgsVectorLayer.getFeatures(selection)
        N = len(selection)
        nivel_inspecao = self.dlg.comboBoxLevel.currentIndex()
        tipo_inspecao = self.dlg.comboBoxType.currentIndex()
        lqa = self.dlg.comboBoxLQA.currentIndex()
        #pop_N, size_n, Ac, letra_codigo_i, letra_codigo_f, msg = sample_plan (N, nivel_inspecao, lqa + 4 , tipo_inspecao)
            
        self.dlg.label_N.setText(str(pop_N))
        self.dlg.label_n.setText(str(size_n))
        self.dlg.label_letra_i.setText(str(letra_codigo_i))
        self.dlg.label_letra_f.setText(str(letra_codigo_f))
        self.dlg.label_msg.setText(str(msg))

        return pop_N, size_n, Ac, letra_codigo_i, letra_codigo_f, msg
    #break 

def list_layers():
    layers = QgsProject.instance().mapLayers().values()
    for layer in layers:
        if layer.type() == 1 :
            if layer.isValid()==True:
                self.dlg.comboBox.addItem( layer.name(), layer )
    return layers 

# Data provider from selection 
# Camada = selection  ###
def data_provider(feature_selected):
    features = QgsVectorLayer.getFeatures(feature_selected)
    dp = feature_selected.dataProvider()
    provider = dp       ###
    geometry = feature_selected.wkbType()
    crs = provider.crs()
    encoding = dp.encoding()
    return features, dp, provider, geometry, crs, encoding 

# Data features from selection 
#lyrInput = QgsVectorLayer.getFeatures(selection) # substituir camada por selection OK
def features_selection(feature_selected): 
    N = 0
    if feature_selected.type() == QgsMapLayer.VectorLayer:
        if feature_selected.isValid()==True:
            features = QgsVectorLayer.getFeatures(feature_selected)
            featureCount = len(feature_selected) # substituir camada por selection - OK
            N = featureCount # população (N)
    return N #, features

def add_fields(provider):
    #fields = QgsFields() # utilizar na inspecao por area 
    fields = provider.fields()
    fields.append(QgsField("id_measure", QVariant.Int))
    fields.append(QgsField("checked", QVariant.String))
    fields.append(QgsField("status", QVariant.String))
    fields.append(QgsField("tx_report", QVariant.String))
    return fields 
    
def sample_features(pop_size, sample_size):
    #randomNum = random.sample(range(featureCount),1)[0]
    isSelectedId = random.sample(range(pop_size), sample_size)
    return isSelectedId

def output_sample(pop_size, sample_size, selection, directory, mensagem, num_aceitacao): 
    if pop_size > sample_size:
        isSelectedId = sample_features(pop_size, sample_size)
        features, dp, provider, geometry, crs, encoding  = data_provider(selection)
        fields = add_fields(dp)
        tipo = "C"
        if mensagem == "inspeção amostral simples":
            tipo = "S"
            Ac, Re = dicAc_simples[num_aceitacao]
            texto_ac_re = "_Ac" + str(Ac) + "_Re" + str(Re) + "_" 

            if Ac == "Utilizar plano de amostragem simples indicado acima" or Ac == "Aceitação não permitida com o tamanho de amostra indicado":
                texto_ac_re = "_NA_"

            if Ac == "Utilizar plano de amostragem simples indicado acima" or Ac == "Aceitação não permitida com o tamanho de amostra indicado":
                texto_ac_re = "_NA_"

        if mensagem == "inspeção amostral dupla": 
            tipo = "D"
            Ac, Re = dicAc_dupla[num_aceitacao]
            texto_ac_re = "_Ac" + str(Ac) + "_Re" + str(Re) + "_" 
            if Ac == "Utilizar plano de amostragem simples indicado acima" or Ac == "Aceitação não permitida com o tamanho de amostra indicado":
                texto_ac_re = "_NA_"

            if Ac == "Utilizar plano de amostragem simples indicado acima" or Ac == "Aceitação não permitida com o tamanho de amostra indicado":
                texto_ac_re = "_NA_"
        if mensagem == "inspeção amostral múltipla": 
            tipo = "M"
            Ac, Re = dicAc_multipla[num_aceitacao]  
            texto_ac_re = "_Ac" + str(Ac) + "_Re" + str(Re) + "_" 
            if Ac == "Utilizar plano de amostragem simples indicado acima" or Ac == "Aceitação não permitida com o tamanho de amostra indicado":
                texto_ac_re = "_NA_"
            if Ac == "Utilizar plano de amostragem simples indicado acima" or Ac == "Aceitação não permitida com o tamanho de amostra indicado":
                texto_ac_re = "_NA_"        
        
        filename = os.path.join(directory + "/sample_" + str(sample_size) + tipo + texto_ac_re + selection.name() +".shp")
        ds = ogr.GetDriverByName("Esri Shapefile")

        file = QgsVectorFileWriter(filename, encoding, fields, geometry, crs, ds.name)

        for i, feat in enumerate(features):
            if i in isSelectedId:
                file.addFeature(feat)
        del file
           
        iface.addVectorLayer(filename, "", "ogr")
        
       
def msg_sample_plan(pop_size, sample_size, num_aceitacao, letra_codigo_i, letra_codigo_f, mensagem, lqa, nivel_inspecao):
    if mensagem == "inspeção amostral simples":
        Ac, Re = dicAc_simples[num_aceitacao]
        #print(Ac, Re, msg)
        # "\n Ac = " + str(Ac) +
        # "\n Re = " + str(Re) +
    if mensagem == "inspeção amostral dupla":
         Ac, Re = dicAc_dupla[num_aceitacao]
    #     #print(Ac, Re, msg)
    #     "\n Ac = " + str(Ac) +
    #     "\n Re = " + str(Re) +
    if mensagem == "inspeção amostral múltipla":
         Ac, Re = dicAc_multipla[num_aceitacao]
    #     #print(Ac, Re, msg)
    #     "\n Ac = " + str(Ac) +
    #     "\n Re = " + str(Re) +
    #"\n Ac = " + str(num_aceitacao) +     
    QMessageBox.about(None, "Sample by feature", str(mensagem) + 
    "\n nivel de inspeção  " + str(id_nivel_inspecao(nivel_inspecao)) +
    "\n LQA = " + str(id_lqa(lqa)) +
    "\n N = " + str(pop_size)+ 
    "\n n = " + str(sample_size) +
    "\n Ac = " + str(Ac) +
    "\n Re = " + str(Re) +
    "\n Letra código (inicial) = " + str(letra_codigo_i) +
    "\n Letra codigo (final) = " + str(letra_codigo_i))
    
def msg_complete(pop_size, sample_size, mensagem):
    QMessageBox.about(None, "Simple random sampling", str(mensagem) + 
    "\n N = " + str(pop_size)+ 
    "\n n = " + str(sample_size) 
    )

def id_lqa(lqa):
    lqa_id = List_LQA[lqa]
    return lqa_id

def id_nivel_inspecao(nivel_inspecao):
    nivel_inspecao_id = List_nivel_inspecao[nivel_inspecao]
    return nivel_inspecao_id

def id_tipo_inspecao(tipo_inspecao):
    tipo_inspecao_id = List_tipo_inspecao[tipo_inspecao]
    return tipo_inspecao_id

"""
### Begin simulation to python terminal
##Input data selection 
selected_layer = iface.activeLayer()
selected_layer.name()
selection = selected_layer
## Sampling plan / Plano de amostragem
nivel_inspecao = 1
tipo_inspecao = 1
lqa = 1
##########
#Directory
#####################
path_project = QgsProject.instance().fileName()
path_project = path_project[:path_project.rfind("/"):]
directory = path_project + "/sample_features"

pth = directory
#####################

###############
# Structure data
################
features, dp, provider, geometry, crs, encoding = data_provider(selection)
###############
###############
# Output #
N = features_selection(selection)
N, n, num_aceitacao, letra_codigo_i, letra_codigo_f, msg = sample_plan (features_selection(selection), nivel_inspecao, lqa + 4 , tipo_inspecao)
print (N, n, num_aceitacao, letra_codigo_i, letra_codigo_f, msg)
print (id_lqa(lqa), id_nivel_inspecao(nivel_inspecao), id_tipo_inspecao(tipo_inspecao))

##########

N, n, num_aceitacao, letra_codigo_i, letra_codigo_f, msg = sample_plan (features_selection(selection), nivel_inspecao, lqa + 4 , tipo_inspecao)

output_sample(N, n, selection, pth)

###########
Mensagem
###########
pop_size = N 
sample_size = n 
if pop_size > sample_size:
    msg_sample_plan( pop_size, sample_size, num_aceitacao, letra_codigo_i, letra_codigo_f, msg, lqa, nivel_inspecao)
        
if pop_size <= sample_size:
    msg_complete( pop_size, sample_size, msg)

############
# End simulation to python terminal   
"""