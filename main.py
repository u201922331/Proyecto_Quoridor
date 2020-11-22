# ##############################################################################
# PROYECTO QUORIDOR
# ##############################################################################
# Integrantes:
#     - Nander Emanuel Melendez Huamanchumo --> u201922331
#     - Dino Iván Pérez Vásquez             --> u201710880
# ##############################################################################

# ******************************************************************************
# LIBRERÍAS
# ******************************************************************************
import pygame, math
import networkx as nx

# ******************************************************************************
# CLASES
# ******************************************************************************
# ------------------------------------------------------------------------------
# Grafo
# ------------------------------------------------------------------------------
class GrafoTablero:
    def __init__(self, ancho=9, alto=9):
        self.G = nx.Graph()

        # Creación de los nodos y conexiones en forma de malla
        E = []

        for i in range(alto):
            for j in range(1, ancho):
                E.append([chr(64 + j) + str(i + 1), chr(65 + j) + str(i + 1), 1])
        for i in range(1, alto):
            for j in range(ancho):
                E.append([chr(65 + j) + str(i), chr(65 + j) + str(i + 1), 1])

        # Agregar las aristas al grafo y, con ello, los vértices
        for e in E:
            self.G.add_edge(e[0], e[1], weight=e[2])

        # Simplificar el acceso a ciertas variables del grafo
        self.actualizar()

    def eliminarCaminos(self, arista):
        if arista not in self.aristas:
            return
        origen, destino = arista[0], arista[1]
        nx.Graph.remove_edge(self.G, origen, destino)

        self.actualizar()

    def actualizar(self):
        def matrizPesos(nodos, aristas, pesos):
            inf = math.inf

            nV, nA = len(nodos), len(aristas)
            pesos_completos = [[inf for x in range(nV)] for y in range(nV)]

            for i in range(nA):
                a, b, p = nodos.index(aristas[i][0]), nodos.index(aristas[i][1]), pesos[i]
                pesos_completos[a][b] = pesos_completos[b][a] = float(p)

            return pesos_completos

        self.nodos, self.aristas = list(self.G.nodes()), list(self.G.edges())
        self.pesos = [self.G.get_edge_data(u, v)['weight'] for [u, v] in self.aristas]
        self.pesos_matriz = matrizPesos(self.nodos, self.aristas, self.pesos)

    def FloydWarshall(self, inicio, final):
        if (inicio not in self.nodos) or (final not in self.nodos):
            return ["-"]
        nV = len(self.nodos)
        P = [[0 for x in range(nV)] for y in range(nV)]

        distancias, v = self.pesos_matriz, len(self.pesos_matriz)
        camino = [inicio]
        vis = [False] * len(self.nodos)

        # Hallar la matriz de caminos cortos y la matriz de camino corto
        for k in range(v):
            for i in range(v):
                for j in range(v):
                    if distancias[i][j] > distancias[i][k] + distancias[k][j]:
                        distancias[i][j] = distancias[i][k] + distancias[k][j]
                        P[i][j] = k
        for i in range(v):
            distancias[i][i] = 0

        # Hallar camino
        def Camino(nodo):
            idxNodo, idxMenor = self.nodos.index(nodo), 0
            vis[idxNodo] = True

            if nodo == final:
                return

            for i in range(len(P[idxNodo])):
                if vis[idxMenor]:
                    idxMenor = (idxMenor + 1) % len(P[idxNodo])

                if not vis[i] and idxNodo != i:
                    if P[idxNodo][i] <= P[idxNodo][idxMenor]:
                        idxMenor = i
            camino.append(self.nodos[idxMenor])

            if not vis[idxMenor]:
                Camino(self.nodos[idxMenor])

        Camino(inicio)

        return camino


# ------------------------------------------------------------------------------
# Posición
# ------------------------------------------------------------------------------
class Posicion:
    def __init__(self, x, y):
        self.x, self.y = x, y


# ------------------------------------------------------------------------------
# Muros
# ------------------------------------------------------------------------------
class Muro:
    def __init__(self, dimensiones_ventana, lados_tablero, color=(90, 17, 15)):
        self.color = color
        self.dimensiones = dimensiones_ventana
        self.lados = lados_tablero


    def dibujar(self):
        pass


# ------------------------------------------------------------------------------
# Jugador
# ------------------------------------------------------------------------------
class Jugador:
    def __init__(self, nombre, orientacion, largo_tablero, tamano=10, num_muros=10):
        def limitar_orientacion(d):
            if d < 0:
                return limitar_orientacion(0)
            elif d > 4:
                return limitar_orientacion(3)
            else:
                return d

        self.orientacion = limitar_orientacion(orientacion)
        self.muros = num_muros
        self.nombre = nombre
        self.tamano = tamano

        ancho, alto = largo_tablero, largo_tablero
        if self.orientacion == 0:
            self.pos = Posicion(ancho // 2, 0)
            self.color = (255, 0, 0)
        elif self.orientacion == 1:
            self.pos = Posicion(ancho // 2, alto - 1)
            self.color = (0, 255, 0)
        elif self.orientacion == 2:
            self.pos = Posicion(ancho - 1, alto // 2)
            self.color = (255, 255, 0)
        else:
            self.pos = Posicion(0, alto // 2)
            self.color = (0, 0, 255)


    def mover(self, tecla):
        ARRIBA, ABAJO, IZQUIERDA, DERECHA = pygame.K_w, pygame.K_s, pygame.K_a, pygame.K_d

        if tecla == ABAJO:
            dx, dy = 0, 1
        elif tecla == ARRIBA:
            dx, dy = 0, -1
        elif tecla == IZQUIERDA:
            dx, dy = -1, 0
        elif tecla == DERECHA:
            dx, dy = 1, 0
        else:
            dx, dy = 0, 0

        self.pos.x += dx
        self.pos.y += dy


    def dibujar(self, ventana, multiplicador=1, calibrar_x=0, calibrar_y=0):
        pygame.draw.circle(ventana, self.color, (multiplicador * self.pos.x + calibrar_x, multiplicador * self.pos.y + calibrar_y), self.tamano)

    def camino_optimo(self, tablero):
        def convertirCoordenadas(punto):
            return chr(65 + punto.x) + str(punto.y + 1)

        origen = self.pos
        if self.orientacion == 0:
            destino = Posicion(origen.x, tablero.lados - 1)
        elif self.orientacion == 1:
            destino = Posicion(origen.x, 0)
        elif self.orientacion == 2:
            destino = Posicion(0, origen.y)
        else:
            destino = Posicion(tablero.lados - 1, origen.y)

        return tablero.grafo.FloydWarshall(convertirCoordenadas(origen), convertirCoordenadas(destino))

# ------------------------------------------------------------------------------
# Tablero
# ------------------------------------------------------------------------------
class Tablero:
    def __init__(self, lados=9):
        self.lados = lados
        self.grafo = GrafoTablero(lados, lados)

    def dibujar_tablero(self, ventana, jugadores, color1=(0, 0, 0), color2=(30, 30, 30)):
        ancho, alto = ventana.get_width() // self.lados, ventana.get_width() // self.lados

        for y in range(self.lados):
            for x in range(self.lados):
                if y % 2 == 0:
                    if x % 2 == 0:
                        color = color1
                    else:
                        color = color2
                else:
                    if x % 2 == 0:
                        color = color2
                    else:
                        color = color1
                pygame.draw.rect(ventana, color, (x * ancho, y * alto, ancho, alto))


        for i in range(len(jugadores)):
            jugadores[i].dibujar(ventana, ancho, ancho // 2, alto // 2)


    def dibujar_tablero_consola(self, lista_jugadores):
        alto, ancho = self.lados, self.lados
        num_jugadores = len(lista_jugadores)

        for i in range(alto):
            linea = ""
            for j in range(ancho):
                c = ""
                for n in range(num_jugadores):
                    if lista_jugadores[n].pos.x == j and lista_jugadores[n].pos.y == i:
                        c = " " + lista_jugadores[n].nombre
                        break
                    else:
                        c = " -"
                linea += c
            print(linea)


# ------------------------------------------------------------------------------
# Juego
# ------------------------------------------------------------------------------
class Juego:
    def __init__(self, dimensiones, tamano_tablero=9):
        self.dimensiones = dimensiones
        self.juego_terminado = False
        self.tablero = Tablero(tamano_tablero)
        self.jugadores = []

    def ejecutar(self, usar_consola = False):
        # Definición de algunas teclas
        ESCAPE = pygame.K_ESCAPE
        ARRIBA, ABAJO, IZQUIERDA, DERECHA = pygame.K_w, pygame.K_s, pygame.K_a, pygame.K_d
        K1, K2, K3, K4, K5, K6, K7, K8, K9, K0 = pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4, pygame.K_5, pygame.K_6, pygame.K_7, pygame.K_8, pygame.K_9, pygame.K_0,

        # Definición de algunos eventos
        SALIR, PRESIONANDO = pygame.QUIT, pygame.KEYDOWN

        # ########################################################################################
        # INICIO del Bloque funciones adicionales
        # vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv
        def cortar_camino(par1, par2):
            self.tablero.grafo.eliminarCaminos(par1)
            self.tablero.grafo.eliminarCaminos(par2)

        def fin_del_juego(jugador, tablero):
            o, x, y = jugador.orientacion, jugador.pos.x, jugador.pos.y
            alto, ancho = tablero.lados, tablero.lados

            return True if (o == 0 and y == alto - 1) or \
                           (o == 1 and y == 0) or \
                           (o == 2 and x == 0) or \
                           (o == 3 and x == ancho - 1) else False

        def mover_jugador(tecla, jugadores, jugador, tablero):
            def coordsToChess(x, y):
                return chr(65 + x) + str(y + 1)

            tu = jugadores[jugador]
            puedo_pasar = True

            for p in jugadores:
                if p != tu:
                    if tecla == IZQUIERDA:           # "not" omitido por cuestiones técnicas
                        if not (tu.pos.x > 0 and (p.pos.y != tu.pos.y or (p.pos.y == tu.pos.y and p.pos.x + 1 != tu.pos.x))) or \
                                [coordsToChess(tu.pos.x, tu.pos.y), coordsToChess(tu.pos.x - 1, tu.pos.y)] in tablero.grafo.aristas:
                            puedo_pasar = False
                            break
                    if tecla == DERECHA:
                        if not (tu.pos.x < tablero.lados - 1 and (p.pos.y != tu.pos.y or (p.pos.y == tu.pos.y and p.pos.x - 1 != tu.pos.x))) or \
                                [coordsToChess(tu.pos.x, tu.pos.y), coordsToChess(tu.pos.x + 1, tu.pos.y)] in tablero.grafo.aristas:
                            puedo_pasar = False
                            break
                    if tecla == ARRIBA:
                        if not (tu.pos.y > 0 and (p.pos.x != tu.pos.x or (p.pos.x == tu.pos.x and p.pos.y + 1 != tu.pos.y))) or \
                                [coordsToChess(tu.pos.x, tu.pos.y), coordsToChess(tu.pos.x, tu.pos.y - 1)] in tablero.grafo.aristas:
                            puedo_pasar = False
                            break
                    if tecla == ABAJO:
                        if not (tu.pos.y < tablero.lados - 1 and (p.pos.x != tu.pos.x or (p.pos.x == tu.pos.x and p.pos.y - 1 != tu.pos.y))) or \
                                [coordsToChess(tu.pos.x, tu.pos.y), coordsToChess(tu.pos.x, tu.pos.y + 1)] in tablero.grafo.aristas:
                            puedo_pasar = False
                            break
            if puedo_pasar:
                tu.mover(tecla)

        def tecla_valida(tecla):
            validas = [IZQUIERDA, DERECHA, ARRIBA, ABAJO, ESCAPE]

            return True if tecla in validas else False

        def actualizar():
            pygame.display.update()

        def esperar(s):
            pygame.time.delay(int(s * 1000))

        # ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
        # FIN del Bloque funciones adicionales
        # ########################################################################################

        # ########################################################################################
        # INICIO del Bloque inicializar ventana
        # vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

        pygame.init()
        ventana = pygame.display.set_mode(self.dimensiones)
        pygame.display.set_caption("Quoridor")
        pygame.display.set_icon(pygame.image.load("recursos/game_icon.png"))
        miFuente = pygame.font.Font(None, 20)

        # ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
        # FIN del Bloque inicializar ventana
        # ########################################################################################

        # ########################################################################################
        # INICIO del Bloque pre-juego
        # vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

        mensaje = miFuente.render("¿Modo de juego? - 1: 2 Jugadores | 2: 4 Jugadores", 0, (255, 255, 255))
        gamemode = 0
        selecting_gamemode = True

        while selecting_gamemode:
            EVENTOS = pygame.event.get()

            ventana.fill((0, 0, 0))
            ventana.blit(mensaje, (30, 100))
            for evento in EVENTOS:
                if evento.type == SALIR:
                    pygame.quit()
                elif evento.type == PRESIONANDO:
                    if evento.key == ESCAPE:
                        exit()
                    else:
                        if evento.key == K1:
                            gamemode = 2
                            selecting_gamemode = False
                        elif evento.key == K2:
                            gamemode = 4
                            selecting_gamemode = False

            actualizar()

        for i in range(gamemode):
            self.jugadores.append(Jugador(str(i), i, self.tablero.lados, self.dimensiones[0] // (4 * self.tablero.lados)))

        mensaje = miFuente.render("TURNO DEL JUGADOR " + self.jugadores[0].nombre, 0, self.jugadores[0].color)
        sugerencia = miFuente.render("CAMINO SUGERIDO: " + str(self.jugadores[0].camino_optimo(self.tablero)), 0, self.jugadores[0].color)

        # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        if usar_consola:
            self.tablero.dibujar_tablero_consola(self.jugadores)
            print("TURNO DEL JUGADOR", self.jugadores[0].nombre)
            print("CAMINO SUGERIDO:", self.jugadores[0].camino_optimo(self.tablero))
        # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

        # ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
        # FIN del Bloque pre-juego
        # ########################################################################################

        ganador, turnos = "", 0
        num_jugadores = len(self.jugadores)

        cortar_camino(["A1", "B1"], ["A2", "B2"])
        cortar_camino(["C1", "D1"], ["C2", "D2"])
        cortar_camino(["A2", "A3"], ["B2", "B3"])
        cortar_camino(["D2", "D3"], ["E2", "E3"])
        cortar_camino(["G2", "H2"], ["G3", "H3"])
        cortar_camino(["H2", "H3"], ["I2", "I3"])
        cortar_camino(["B4", "C4"], ["B5", "C5"])
        cortar_camino(["E4", "E5"], ["F4", "F5"])
        cortar_camino(["G4", "H4"], ["G5", "H5"])
        cortar_camino(["A6", "A7"], ["B6", "B7"])
        cortar_camino(["C6", "C7"], ["D6", "D7"])
        cortar_camino(["H6", "I6"], ["H7", "I7"])
        cortar_camino(["C7", "D7"], ["C8", "D8"])
        cortar_camino(["E8", "E9"], ["F8", "F9"])
        cortar_camino(["F8", "G8"], ["F9", "G9"])

        # ########################################################################################
        # INICIO del Bloque juego
        # vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv
        while not self.juego_terminado:
            ventana.fill((0, 0, 0))
            self.tablero.dibujar_tablero(ventana, self.jugadores)
            ventana.blit(mensaje, (30, 610))
            ventana.blit(sugerencia, (30, 625))
            EVENTOS = pygame.event.get()

            # 1. Determinar si alguno de los jugadores ha ganado
            for i in range(num_jugadores):
                if fin_del_juego(self.jugadores[i], self.tablero):
                    self.juego_terminado = True
                    ganador += self.jugadores[i].nombre
                    break
            # 2. Continuar con el juego mientras que nadie haya ganado
            if not self.juego_terminado:
                # NOTA: Por el momento todos los jugadores se controlarán de forma manual
                for evento in EVENTOS:
                    if evento.type == SALIR:
                        pygame.quit()
                    elif evento.type == PRESIONANDO:
                        mover_jugador(evento.key, self.jugadores, turnos % num_jugadores, self.tablero)

                        if tecla_valida(evento.key):
                            if evento.key == ESCAPE:
                                exit()
                            turnos += 1

                        mensaje = miFuente.render("TURNO DEL JUGADOR " + self.jugadores[turnos % num_jugadores].nombre, 0, self.jugadores[turnos % num_jugadores].color)
                        sugerencia = miFuente.render("CAMINO SUGERIDO: " + str(self.jugadores[turnos % num_jugadores].camino_optimo(self.tablero)), 0, self.jugadores[turnos % num_jugadores].color)

                        # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
                        if usar_consola:
                            self.tablero.dibujar_tablero_consola(self.jugadores)
                            print("TURNO DEL JUGADOR", self.jugadores[turnos % num_jugadores].nombre)
                            print("CAMINO SUGERIDO:", self.jugadores[turnos % num_jugadores].camino_optimo(self.tablero))
                        # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

            actualizar()

        # ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
        # FIN del Bloque juego
        # ########################################################################################

        # ########################################################################################
        # INICIO del Bloque post-juego
        # vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvv

        # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        if usar_consola:
            self.tablero.dibujar_tablero_consola(self.jugadores)
            print("¡El ganador es el jugador: " + ganador + "!")
        # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

        ventana.fill((0, 0, 0))
        self.tablero.dibujar_tablero(ventana, self.jugadores)
        mensaje = miFuente.render("¡El ganador es el jugador " + ganador + "!", 0, (255, 255, 255))
        ventana.blit(mensaje, (30, self.dimensiones[0] + 10))
        actualizar()

        esperar(3)
        # ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
        # FIN del Bloque post-juego
        # ########################################################################################


# ******************************************************************************
# FUNCIÓN PRINCIPAL
# ******************************************************************************
def main():
    quoridor = Juego((600, 650))
    quoridor.ejecutar()


# ******************************************************************************
# INICIALIZADOR
# ******************************************************************************
if __name__ == '__main__':
    main()
