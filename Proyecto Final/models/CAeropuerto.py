import pandas as pd
import folium 
import graphviz as gv
from models.algoritmos import CAStar
class CAeropuerto:
    def __init__(self):
       self.Nodos = pd.read_excel("ds/Nodos2.xlsx")
       self.Aristas = pd.read_excel("ds/Aristas.xlsx")
       self.listNodos = []
       self.listAristas = []
       self.lat_long_iata = {}
       self.aStarDict = {}
       self.filterData()
       self.init_lat_long()
       self.initAStarDict()
    

    def filterData(self): 
        self.Nodos   = self.Nodos.dropna()
        self.Nodos   = self.Nodos.reset_index(drop=True)
        self.Nodos   = self.Nodos.sort_index()

        self.Aristas = self.Aristas.dropna()
        #self.Aristas = self.Aristas.reset_index(drop=True)
        #self.Aristas = self.Aristas.drop(range(500, len(self.Aristas)))
        self.Aristas = self.Aristas.drop('Precio', axis = 1)
        self.Aristas = self.Aristas.reset_index(drop=True)
        self.Aristas = self.Aristas.sort_index()

    def init_lat_long(self):
        for i in range(len(self.Nodos)):
            nodo = self.Nodos.IATA[i]
            self.lat_long_iata[nodo] = [self.Nodos.Latitude[i], self.Nodos.Longitude[i]]
            #self.listNodos.append(nodo)
            self.listNodos.append({
                'IATA' : nodo,
                'City' : self.Nodos.City[i],
                'Country' : self.Nodos.Country[i]
            })

    def initAStarDict(self):
        for i in range(len(self.Nodos)):
            self.aStarDict[self.Nodos.IATA[i]] = []

        for i in self.aStarDict.keys():
            resultado  = self.Aristas[self.Aristas['Ciudad_Origen'] == i]
            resultado = resultado.reset_index(drop=True)
            for j in range(len(resultado)):
                if(resultado.Ciudad_Destino[j] in self.aStarDict.keys()):
                  self.aStarDict[i].append((resultado.Ciudad_Destino[j], resultado.PrecioP[j]))
                  self.aStarDict[resultado.Ciudad_Destino[j]].append(( i , resultado.PrecioP[j]))
                  if (i,resultado.Ciudad_Destino[j]) not in self.listAristas:
                    self.listAristas.append((i,resultado.Ciudad_Destino[j]))
    
    def calcMiniumPrice(self, iata1:str, iata2:str, airportsavoided = []):
        return CAStar.miniumCostAstar(self.aStarDict, iata1, iata2, airportsavoided)
    
    def agregar_nodo_resultante(self, map, latitud, longitud, nodoName):
        newNodo = folium.Marker(location=[latitud, longitud], popup = nodoName)
        newNodo.add_to(map)
    
    def agregar_camino_resultante(self, map, arr_camino):
        for i in range(len(arr_camino) - 1):
          CoordsOrigen  = self.lat_long_iata[arr_camino[i]]
          CoordsDestino = self.lat_long_iata[arr_camino[i+1]]
          precio = 0
          for tupla in self.aStarDict[arr_camino[i]]:
            if tupla[0] == arr_camino[i+1]:
                precio = tupla[1]
                break
          arista = folium.PolyLine(      
              locations=[CoordsOrigen, CoordsDestino],
              color='red',
              weight= 3,
              tooltip=f'Precio: {precio}'
            )
          arista.add_to(map)
        for j in range(len(arr_camino)):
          Coords  = self.lat_long_iata[arr_camino[j]]
          filaDF = self.Nodos.loc[self.Nodos['IATA'] == arr_camino[j]]
          filaDF = filaDF.reset_index()
          self.agregar_nodo_resultante(map, Coords[0], Coords[1], f"{filaDF.City[0]}, {filaDF.Country[0]}, {filaDF.IATA[0]}")


    def getMapaResult(self, origen, destino, airportsAvoided = []):
        route = self.calcMiniumPrice(origen, destino, airportsAvoided)
        mapa = folium.Map(location=[0, 0], zoom_start = 2)
        self.agregar_camino_resultante(mapa, route)
        precio = 0
        for i in range(len(route)-1):
            for tupla in self.aStarDict[route[i]]:
                if tupla[0] == route[i+1]:
                    precio += tupla[1]
                    break
        return mapa, precio
    
    def deleteRoute(self, origen, destino):
        if((origen, destino) in self.listAristas or (destino, origen) in self.listAristas):
            #dict1['LIM'] = [ruta for ruta in dict1['LIM'] if ruta[0] != 'AYP']
            self.aStarDict[origen] = [ruta for ruta in self.aStarDict[origen] if ruta[0] != destino]
            self.aStarDict[destino] = [ruta for ruta in self.aStarDict[destino] if ruta[0] != origen]
            return True
        return 
    
    def agregar_arista(self, map, CoordsOrigen, CoordsDest, peso = 99999):
        # Agregar aristas al mapa con pesos
        arista = folium.PolyLine(
          #locations=[[40.7128, -74.0060], [40.7216, -74.0045]],
          locations=[CoordsOrigen, CoordsDest],
          color='blue',
          weight=1,
          tooltip=f'Precio: {peso}'
        )
        arista.add_to(map)

    def agregar_nodo(self, map, latitud, longitud, nodoName):
        newNodo = folium.Marker(location=[latitud, longitud], popup=nodoName)
        newNodo.add_to(map)

    def showCompleteMap(self):
        mapa = folium.Map(location=[-12.0219, -77.114305], zoom_start = 3)
        for i in self.listNodos:
            lat = self.lat_long_iata[i][0]
            long = self.lat_long_iata[i][1]
            self.agregar_nodo(mapa, lat, long, i)

        for i in self.listAristas:
            origen, destino = i
            coordsOrigen = self.lat_long_iata[origen]
            coordsDestino = self.lat_long_iata[destino]
            precio = 0
            for tupla in self.aStarDict[origen]:
                if tupla[0] == destino:
                    precio = tupla[1]
                    break
            self.agregar_arista(mapa,coordsOrigen,coordsDestino,precio)

        mapa.save("templates/mapaComplete.html")
        return
    
    def get_graph(self, origen, destino, airportsAvoided):
        route = self.calcMiniumPrice(origen, destino, airportsAvoided)

        # Crea un objeto Digraph de Graphviz
        dot = gv.Graph()

        # Agrega nodos y aristas a tu gráfico
        for i in range(len(route)):
            dot.node(str(route[i]))
        for i in range(len(route)):
            if(i == len(route) - 1):continue
            precio = 0
            for tupla in self.aStarDict[route[i]]:
                if tupla[0] == route[i+1]:
                    precio = tupla[1]
                    break
            dot.edge(str(route[i]), str(route[i+1]), str(precio))

        dot.render('static/graph', format='png')
        output_file = 'static/img/grafo'
        dot.format = 'png'
        dot.render(filename = output_file, cleanup=True)

        return 'static/img/grafo.png'

            



                      

    
