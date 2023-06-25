import heapq
class CAStar:
    def __init__(self):
        pass

    @classmethod
    def miniumCostAstar(cls, grafo, inicio, destino, listAvoided = []):
        cola_prioridad = []
        heapq.heappush(cola_prioridad, (0, inicio))
        costo_g = {inicio: 0}
        costo_f = {inicio: 0}
        padre = {inicio: None}
    
        while cola_prioridad:
            _, nodo_actual = heapq.heappop(cola_prioridad)
    
            if nodo_actual == destino:
                break
            
            for nodo_siguiente, peso_arista in grafo[nodo_actual]:
                if nodo_siguiente in listAvoided:
                    continue
                costo_nuevo = costo_g[nodo_actual] + peso_arista
    
                if nodo_siguiente not in costo_g or costo_nuevo < costo_g[nodo_siguiente]:
                    costo_g[nodo_siguiente] = costo_nuevo
                    costo_f[nodo_siguiente] = costo_nuevo
                    padre[nodo_siguiente] = nodo_actual
                    heapq.heappush(cola_prioridad, (costo_f[nodo_siguiente], nodo_siguiente))
    
        camino = []
        nodo_actual = destino
    
        if nodo_actual not in padre:
            print("No hay camino disponible")
            return camino
    
        while nodo_actual:
            camino.insert(0, nodo_actual)
            nodo_actual = padre[nodo_actual]
    
        return camino