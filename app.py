import tkinter as tk
import networkx as nx
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
from config import Config


class GraphDisplay:
    def __init__(self, root):
        self.root = root
        self.root.title("Interactive NetworkX Graph")

        self.canvas_frame = tk.Frame(root)
        self.canvas_frame.pack(pady=5)

        self.fig = plt.figure(figsize=(5, 5))
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.canvas_frame)
        self.canvas.get_tk_widget().pack()

        self.graph = nx.Graph()
        self.positions = None
        self.selected_node = None
        self.hovered_node = None

        self.canvas.mpl_connect('button_press_event', self.on_click)
        self.canvas.mpl_connect('motion_notify_event', self.on_hover)

        self.draw_graph(first_drawing=True)

    def draw_graph(self, first_drawing=False):
        """
        rysuje graf

        :param first_drawing: czy to pierwszy raz, kiedy rysowany jest graf
        :return: draw graph
        """
        self.fig.gca().clear()  # Clear the previous plot

        if first_drawing:
            self.graph.add_nodes_from(range(1, Config.N_VERTICES))
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

        self.canvas.draw()

    def draw_custom_nodes(self, nodes=None, color='skyblue', border_color=None):
        """ draws nodes with custom settings """
        if nodes is None:
            nodes = self.graph.nodes
        nx.draw_networkx_nodes(self.graph, self.positions, nodelist=nodes,
                               node_color=color, node_size=700, ax=self.fig.gca(), edgecolors=border_color)

    def on_click(self, event):
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
                        self.selected_node = None

                    else:
                        # komunikat w okienku
                        print("Edge already exists.")

                self.draw_graph()

    def on_hover(self, event):
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
        Znajduje odpowiedni wierzchołek, na który nakierowany jest kursor
        """
        node = None
        for n, (xpos, ypos) in self.positions.items():
            if (x - Config.RADIUS <= xpos <= x + Config.RADIUS) and (y - Config.RADIUS <= ypos <= y + Config.RADIUS):
                node = n
                break
        return node


if __name__ == "__main__":
    app_root = tk.Tk()
    app = GraphDisplay(app_root)
    app_root.mainloop()
