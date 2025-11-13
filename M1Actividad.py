from mesa import Agent, Model  # Agent define comportamiento individual, Model define el entorno global
from mesa.space import MultiGrid  # MultiGrid permite representar la habitación como una cuadrícula MxN
from mesa.datacollection import DataCollector  # DataCollector sirve para registrar datos del modelo automáticamente
import random


# Define el Agente

class VacuumAgent(Agent):  # Hereda de mesa.Agent
    def __init__(self, unique_id, model):
        super().__init__(model)  # Agent solo recibe el modelo como parámetro
        self.unique_id = unique_id  # Guarda el ID manualmente para identificar agentes
        self.moves = 0  # Contador de movimientos realizados por el agente

    def step(self):  # Método que define el comportamiento del agente en cada tick de la simulación
        x, y = self.pos  # Posición actual del agente en la cuadrícula

        # Si la celda actual está sucia la limpia
        if (x, y) in self.model.dirty_cells:
            self.model.dirty_cells.remove((x, y))
            print(f"Agente {self.unique_id} limpió la celda ({x+1},{y+1})")
            return

        # Si está limpia intenta moverse a una celda vecina
        neighbors = self.model.grid.get_neighborhood(
            self.pos, moore=True, include_center=False, radius=1
        )
        valid_neighbors = [pos for pos in neighbors if not self.model.grid.out_of_bounds(pos)]
        if valid_neighbors:
            new_position = random.choice(valid_neighbors)
            self.model.grid.move_agent(self, new_position)
            self.moves += 1
        else:
            print(f"Agente {self.unique_id} no pudo moverse (borde del mapa)")


# Definición del Modelo (entorno)

class VacuumModel(Model):
    def __init__(self, M, N, num_agents, porcentaje_sucias, tiempo_max):
        super().__init__()  # Inicializa internamente las estructuras de Mesa
        self.grid = MultiGrid(M, N, torus=False)  # MultiGrid crea la cuadrícula donde viven los agentes
        self.tiempo_max = tiempo_max
        self.num_agents = num_agents
        self.M = M
        self.N = N

        # Inicialización de celdas sucias (aleatorias)
        total_celdas = M * N
        num_sucias = int(total_celdas * porcentaje_sucias / 100)
        self.dirty_cells = set()
        while len(self.dirty_cells) < num_sucias:
            x = self.random.randrange(M)
            y = self.random.randrange(N)
            self.dirty_cells.add((x, y))
        print(f"Celdas sucias iniciales: {len(self.dirty_cells)} ({porcentaje_sucias}%)")

        # Crea agentes en [1,1]
        self.agents_list = []
        for i in range(num_agents):
            a = VacuumAgent(i, self)
            self.agents_list.append(a)
            self.grid.place_agent(a, (0, 0))  # place_agent() posiciona el agente en la cuadrícula
        print(f"Todos los agentes inician en la celda (1,1)")

        # Contadores globales
        self.step_count = 0
        self.total_moves = 0

    def step(self):  # Se ejecuta una vez por tick
        # Activar cada agente (en orden aleatorio)
        random.shuffle(self.agents_list)
        for agent in self.agents_list:
            agent.step()
            self.total_moves += agent.moves
            agent.moves = 0  # reset parcial para no duplicar conteos en siguiente iteración

        self.step_count += 1

        # Terminar si ya no hay celdas sucias o alcanzamos el tiempo máximo
        if not self.dirty_cells or self.step_count >= self.tiempo_max:
            self.running = False


if __name__ == "__main__":
    M = int(input("Ingresa el número de filas (M): "))
    N = int(input("Ingresa el número de columnas (N): "))
    num_agents = int(input("Ingresa el número de agentes: "))
    porcentaje_sucias = float(input("Ingresa el porcentaje de celdas sucias (0-100): "))
    tiempo_max = int(input("Ingresa el tiempo máximo de ejecución (en pasos): "))

    model = VacuumModel(M, N, num_agents, porcentaje_sucias, tiempo_max)

    print("\n Iniciando simulación")
    while getattr(model, "running", True):
        model.step()
        print(f"Paso {model.step_count}: {len(model.dirty_cells)} celdas sucias restantes")


    
    total_celdas = M * N
    limpias = total_celdas - len(model.dirty_cells)
    porcentaje_limpias = (limpias / total_celdas) * 100

    print("\nSimulación terminada")
    print(f"Tiempo total ejecutado: {model.step_count} pasos")
    print(f"Celdas limpias al final: {limpias}/{total_celdas} ({porcentaje_limpias:.2f}%)")
    print(f"Movimientos totales realizados por todos los agentes: {model.total_moves}")