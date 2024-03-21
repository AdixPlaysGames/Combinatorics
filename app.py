import tkinter as tk
import networkx as nx
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
from config import Config
import random


class GraphDisplay:
    def __init__(self, root):
        self.root = root
        self.root.title("Interactive NetworkX Graph")

        window_height = 620
        window_width = 600
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x_cordinate = int((screen_width / 2) - (window_width / 2))
        y_cordinate = int((screen_height / 2) - (window_height / 2))
        self.root.geometry("{}x{}+{}+{}".format(window_width, window_height, x_cordinate, y_cordinate))

        self.pause_button = tk.Button(root, text="Pause", command=self.pause_app)
        self.pause_button.pack(pady=5, padx=10, anchor='nw')

        self.canvas_frame = tk.Frame(root)
        self.canvas_frame.pack(pady=(0, 10), padx=10)

        self.fig = plt.figure(figsize=(6, 6))
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.canvas_frame)
        self.canvas.get_tk_widget().pack(pady=1, padx=1)

        self.graph = nx.Graph()
        self.positions = None
        self.selected_node = None
        self.hovered_node = None
        self.color1_edges = []
        self.color2_edges = []

        self.canvas.mpl_connect('button_press_event', self.on_click)
        self.canvas.mpl_connect('motion_notify_event', self.on_hover)

        self.draw_graph(first_drawing=True)

        self.pause_menu = None

    def pause_app(self):
        """ pause button handler """
        self.show_pause_menu()

    def show_pause_menu(self):
        """ shows pause menu """
        self.pause_menu = tk.Toplevel(self.root)
        self.pause_menu.title("Pause Menu")

        self.root.eval(f'tk::PlaceWindow {str(self.pause_menu)} center')

        pause_menu_width = 200
        pause_menu_height = 150
        self.pause_menu.geometry(f"{pause_menu_width}x{pause_menu_height}")

        info_label = tk.Label(self.pause_menu, text="Game paused")
        info_label.pack()

        resume_button = tk.Button(self.pause_menu, text="Resume", command=self.pause_menu.destroy)
        resume_button.pack(pady=5)
        restart_button = tk.Button(self.pause_menu, text="Restart", command=self.restart_game)
        restart_button.pack(pady=5)
        exit_button = tk.Button(self.pause_menu, text="Exit", command=self.quit_game)
        exit_button.pack(pady=5)

        self.pause_menu.transient(self.root)
        self.pause_menu.grab_set()
        self.root.wait_window(self.pause_menu)

    def quit_game(self):
        """ quits the game """
        self.pause_menu.destroy()
        self.root.quit()

    def restart_game(self):
        """ restarts the game """
        self.reset_game()
        self.pause_menu.destroy()

    def draw_graph(self, first_drawing=False):
        """
        draws graph with nodes

        :param first_drawing: if it is the first time the graph is drawn
        :return: draws graph
        """
        ax = self.fig.gca()  # Clear the previous plot
        ax.clear()

        if first_drawing:
            self.graph.add_nodes_from(range(1, Config.N_VERTICES+1))
        self.positions = nx.circular_layout(self.graph)

        nx.draw(self.graph, self.positions, with_labels=True, node_size=700, node_color='skyblue',
                font_size=10, font_weight='bold', ax=self.fig.gca())

        if self.selected_node is not None:
            self.draw_custom_nodes(nodes=[self.selected_node], color='orange')

        if self.hovered_node is not None:
            if self.hovered_node == self.selected_node:
                self.draw_custom_nodes(nodes=[self.hovered_node], color='orange', border_color='black')
            else:
                self.draw_custom_nodes(nodes=[self.hovered_node], border_color='black')

        self.draw_custom_edges(edges=self.color1_edges)
        self.draw_custom_edges(edges=self.color2_edges, color='blue')

        self.canvas.draw()

    def draw_custom_nodes(self, nodes=None, color='skyblue', border_color=None):
        """ draws nodes with custom settings """
        if nodes is None:
            nodes = self.graph.nodes
        nx.draw_networkx_nodes(self.graph, self.positions, nodelist=nodes,
                               node_color=color, node_size=700, ax=self.fig.gca(), edgecolors=border_color)

    def draw_custom_edges(self, edges=None, color='red'):
        """ draws edges with custom settings """
        if edges is None:
            edges = self.graph.edges
        if len(edges) == 0:
            return
        nx.draw_networkx_edges(self.graph, self.positions, edgelist=edges, edge_color=color)

    def on_click(self, event):
        """ actions for mouse click """
        if event.inaxes is not None:  # sprawdzenie czy zdarzenie odbyło się w obrębie grafu
            x, y = event.xdata, event.ydata
            node = self.find_node(x, y)

            if node is not None:
                if self.selected_node is None:
                    # jeśli nie ma zaznaczonego, to zaznaczamy
                    self.selected_node = node
                else:
                    if self.selected_node == node:
                        # jeśli był zaznaczony, to odznaczamy
                        self.selected_node = None

                    elif not self.graph.has_edge(self.selected_node, node):
                        # jeśli nie ma krawędzi, to dodajemy
                        self.graph.add_edge(self.selected_node, node)
                        self.color_edge(edge=(self.selected_node, node))
                        self.selected_node = None
                        self.check_game()
                    else:
                        # komunikat w okienku
                        print("Edge already exists.")

                self.draw_graph()

    def on_hover(self, event):
        """ actions for mouse hover """
        if event.inaxes is not None:
            x, y = event.xdata, event.ydata
            node = self.find_node(x, y)

            if node is not None:
                self.hovered_node = node
                self.draw_graph()

            elif self.hovered_node is not None and node is None:
                self.hovered_node = None
                self.draw_graph()

    def find_node(self, x, y):
        """
        finds a node, which is being pointed at by cursor
        """
        node = None
        for n, (xpos, ypos) in self.positions.items():
            if (x - Config.RADIUS <= xpos <= x + Config.RADIUS) and (y - Config.RADIUS <= ypos <= y + Config.RADIUS):
                node = n
                break
        return node

    def color_edge(self, edge):
        """ painter strategy logic """
        if random.randint(0, 1) == 0:
            self.color1_edges.append(edge)
        else:
            self.color2_edges.append(edge)

    def check_game(self):
        """ checks game state """
        if is_complete(self.graph):
            self.reset_game()

    def reset_game(self):
        """ resets game """
        self.graph = nx.Graph()
        self.positions = None
        self.selected_node = None
        self.hovered_node = None
        self.color1_edges = []
        self.color2_edges = []
        self.draw_graph(first_drawing=True)


def is_complete(G):
    """ checks if graph G is complete """
    n = G.order()
    return n*(n-1)/2 == G.size()


if __name__ == "__main__":
    app_root = tk.Tk()
    app = GraphDisplay(app_root)
    app_root.mainloop()
