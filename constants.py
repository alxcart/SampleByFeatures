#CONSTANTS
from qgis.core import *
# Sampling plan / Plano de amostragem
#Inspection level / Nivel_de_Inspecao = self.dlg.comboBoxLevel.currentIndex()
#dicSampleLength={2:[2,2,3],9:[2,3,5],16:[3,5,8],26:[5,8,13],51:[5,13,20],91:[8,20,32],151:[13,32,50],281:[20,50,80],501:[32,80,125],1201:[50,125,200],3201:[80,200,315],10001:[125,315,500],35001:[200,500,800],150001:[315,800,1250],500001:[500,1250,2000]}


dicAc_dupla = {0:["Utilizar plano de amostragem simples indicado acima", "Utilizar plano de amostragem simples indicado acima"], 1:[0, 2], 2:[0, 3], 3:[1, 4], 5:[2, 5], 7:[3, 7], 8:[3, 7], 10:[5, 9], 12:[6, 10], 14:[7, 11], 18:[9, 14],21:[11, 16]}
dicAc_simples = {0:[0, 1], 1:[1, 2], 2:[2, 3], 3:[3, 4], 5:[5, 6], 7:[7, 8], 8:[8, 9], 10:[10, 11], 12:[12, 13], 14:[14, 15], 18:[18, 19],21:[21, 22]}
dicAc_multipla = {0:["Utilizar plano de amostragem simples indicado acima","Utilizar plano de amostragem simples indicado acima"], 1: ["", 2], 2: ["Aceitação não permitida com o tamanho de amostra indicado", 2], 3: ["Aceitação não permitida com o tamanho de amostra indicado", 3], 5: ["Aceitação não permitida com o tamanho de amostra indicado", 4], 7: [0, 4], 8: [0, 4], 10: [0, 5], 12: [0, 6], 14: [1, 7], 18: [1, 8],21: [2, 9]}

# Map Units
Meters                  = 0
Feet                    = 1
Degrees                 = 2
UnknownUnit             = 3
DecimalDegrees          = 4
DegreesMinutesSeconds   = 5
DegreesDecimalMinutes   = 6
NauticalMiles           = 7


uMeters                 = QgsUnitTypes.DistanceMeters 	        #Meters.
uKilometers             = QgsUnitTypes.DistanceKilometers 	    #Kilometers.
uImperialFeet           = QgsUnitTypes.DistanceFeet 	        #Imperial feet.
uNauticalMiles          = QgsUnitTypes.DistanceNauticalMiles 	#Nautical miles.
uImperialYards          = QgsUnitTypes.DistanceYards 	        #Imperial yards.
uTerrestrialMiles       = QgsUnitTypes.DistanceMiles 	        #Terrestrial miles.
uDegrees                = QgsUnitTypes.DistanceDegrees 	        #Degrees, for planar geographic CRS distance measurements.
uCentimeters            = QgsUnitTypes.DistanceCentimeters 	    #Centimeters.
uMillimeters            = QgsUnitTypes.DistanceMillimeters 	    #Millimeters.
uUnknownDistanceUnit    = QgsUnitTypes.DistanceUnknownUnit 	    #Unknown distance unit.

#Convert km to
#Meter
m = 1000

#Feet
ft = 3280.8398950131

#Degrees
dg = 1/111.320

#NauticalMiles
nm = 0.54

#UnknownUnit
uk = 1