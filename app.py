import tkinter as tk
import networkx as nx
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
from config import Config
import random
from strategy import is_complete, check_monochromatic_clique


class RamseyGame:
    """
    Attributes
    ----------
    root : tk.Tk()
        main app window
    pause_button : tk.Button
        menu display button
    graph : nx.Graph
        main game graph
    positions :
        node positions
    selected_node : int
        id of currently selected node
    hovered_node : int
        id of currently hovered node
    color1_edges : List
        edges colored with first color
    color2_edges : List
        edges colored with second color
    n_vertices : int
        number of vertices of the main graph
    clique_size : int
        number of vertices of the desired clique
    n_vertices_ent : tk.Entry
        placeholder for n_vertices value
    clique_size_ent : tk.Entry
        placeholder for clique_size value
    click_id :
         mouse click handler id, for connecting and disconnecting
    hover_id :
        mouse hover handler id, for connecting and disconnecting
    pause_menu : tk.TopLevel
        game menu
    start_menu : tk.TopLevel
        starting menu where you can enter game parameters
    start_menu_info_label : tk.Label
        a label for displaying validation info
    """

    def __init__(self, root):

        self.root = root
        self.root.title("Ramsey Numbers Online")

        # set dimensions and center
        window_height = 620
        window_width = 600
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x_cordinate = int((screen_width / 2) - (window_width / 2))
        y_cordinate = int((screen_height / 2) - (window_height / 2))
        self.root.geometry("{}x{}+{}+{}".format(window_width, window_height, x_cordinate, y_cordinate))

        self.pause_button = tk.Button(root, text="Menu", command=self.pause_app)
        self.pause_button.pack(pady=5, padx=10, anchor='nw')

        # prepare canvas for drawing graph
        self.canvas_frame = tk.Frame(root)
        self.canvas_frame.pack(pady=(0, 10), padx=10)

        self.fig = plt.figure(figsize=(6, 6))
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.canvas_frame)
        self.canvas.get_tk_widget().pack(pady=1, padx=1)

        # initialize all game attributes
        self.graph = nx.Graph()
        self.positions = None
        self.selected_node = None
        self.hovered_node = None
        self.color1_edges = []
        self.color2_edges = []
        self.n_vertices = 5
        self.clique_size = 3
        self.n_vertices_ent = None
        self.clique_size_ent = None

        # ids for event handlers
        self.click_id = self.canvas.mpl_connect('button_press_event', self.on_click)
        self.hover_id = self.canvas.mpl_connect('motion_notify_event', self.on_hover)

        self.pause_menu = None
        self.start_menu = None
        self.start_menu_info_label = None

        self.show_start_menu()

    """ APP UI """

    def show_pause_menu(self, finish_info=None):
        """ shows pause menu """
        self.pause_menu = tk.Toplevel(self.root)
        self.pause_menu.title("Menu")
        self.root.eval(f'tk::PlaceWindow {str(self.pause_menu)} center')
        self.pause_menu.geometry(f"{Config.MENU_WIDTH}x{Config.MENU_HEIGHT}")

        # if game has finished show results otherwise display 'resume' button
        if finish_info is None:
            resume_button = tk.Button(self.pause_menu, text="Resume", command=self.pause_menu.destroy, height=1, width=10)
            resume_button.pack(pady=(10, 5))
        else:
            finished_label = tk.Label(self.pause_menu, text=finish_info)
            finished_label.pack(pady=(10, 5))
        restart_button = tk.Button(self.pause_menu, text="Restart", command=self.restart_game, height=1, width=10)
        restart_button.pack(pady=5)
        new_game_button = tk.Button(self.pause_menu, text="New game", command=self.menu_new_game, height=1, width=10)
        new_game_button.pack(pady=5)
        exit_button = tk.Button(self.pause_menu, text="Exit", command=self.menu_quit_game, height=1, width=10)
        exit_button.pack(pady=5)

        self.pause_menu.transient(self.root)
        self.pause_menu.grab_set()
        self.root.wait_window(self.pause_menu)

    def show_start_menu(self):
        """ shows start menu """
        self.start_menu = tk.Toplevel(self.root)
        self.start_menu.title("Menu")
        self.root.eval(f'tk::PlaceWindow {str(self.start_menu)} center')
        self.start_menu.geometry(f"{Config.MENU_WIDTH}x{Config.MENU_HEIGHT}")

        vertices_label = tk.Label(self.start_menu, text='Enter number of vertices')
        vertices_label.pack(pady=(5, 0))
        self.n_vertices_ent = tk.Entry(self.start_menu)
        self.n_vertices_ent.pack()
        clique_label = tk.Label(self.start_menu, text='Enter clique size')
        clique_label.pack(pady=(5, 0))
        self.clique_size_ent = tk.Entry(self.start_menu)
        self.clique_size_ent.pack()
        self.start_menu_info_label = tk.Label(self.start_menu, text="\n")
        self.start_menu_info_label.pack()

        restart_button = tk.Button(self.start_menu, text="Start game", command=self.start_game, height=1, width=10)
        restart_button.pack(pady=5)

        self.start_menu.transient(self.root)
        self.start_menu.grab_set()
        self.root.wait_window(self.start_menu)

    """ BUTTON HANDLERS """

    def pause_app(self):
        """ pause button handler """
        self.show_pause_menu()

    def menu_quit_game(self):
        """ quits the game """
        self.pause_menu.destroy()
        self.root.quit()

    def menu_new_game(self):
        """ new game handler """
        self.show_start_menu()
        self.pause_menu.destroy()

    def start_game(self):
        """ starts the game"""
        validation, info = self.validate_params()
        if not validation:
            self.start_menu_info_label.config(text=info)
            return
        self.reset_game()
        self.start_menu.destroy()

    def restart_game(self):
        """ restarts the game """
        self.reset_game()
        self.pause_menu.destroy()

    """ GRAPH ACTIONS """

    def draw_graph(self, first_drawing=False):
        """
        draws graph with nodes

        :param first_drawing: if it is the first time the graph is drawn
        :return: draws graph
        """
        ax = self.fig.gca()  # Clear the previous plot
        ax.clear()

        if first_drawing:
            self.graph.add_nodes_from(range(1, self.n_vertices+1))
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

    """ GAMEPLAY & GAME LOGIC """

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
                        self.draw_graph()
                        self.check_game()
                        return
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
        if check_monochromatic_clique(self.graph, self.clique_size):
            self.end_game("User won :)")
        if is_complete(self.graph):
            self.end_game("Computer won :(")

    def end_game(self, info):
        """ ends game, disables interaction, shows results """
        self.canvas.mpl_disconnect(self.click_id)
        self.canvas.mpl_disconnect(self.hover_id)
        self.show_pause_menu(finish_info=info)

    def reset_game(self):
        """ resets game, connects interaction back """
        self.graph = nx.Graph()
        self.positions = None
        self.selected_node = None
        self.hovered_node = None
        self.color1_edges = []
        self.color2_edges = []
        self.canvas.mpl_connect('button_press_event', self.on_click)
        self.canvas.mpl_connect('motion_notify_event', self.on_hover)
        self.draw_graph(first_drawing=True)

    """ UTILS """

    def disable_event(self, event=None):
        """ disables event if needed """
        pass

    def set_parameters(self, n_vertices, clique_size):
        """ sets game parameters """
        self.n_vertices = n_vertices
        self.clique_size = clique_size

    def validate_params(self):
        """ validates and sets params, returns a tuple (bool, string) """
        try:
            print(self.n_vertices)
            print(self.clique_size)
            n_vertices = int(self.n_vertices_ent.get())
            clique_size = int(self.clique_size_ent.get())
        except ValueError:
            return False, "input must be an integer"

        try:
            assert n_vertices > 1
            assert clique_size > 1
        except AssertionError:
            return False, "input must be bigger than 1"

        try:
            assert n_vertices >= clique_size
        except AssertionError:
            return False, "clique size cant be bigger\nthan number of vertices"

        self.set_parameters(n_vertices, clique_size)
        return True, ""


if __name__ == "__main__":
    app_root = tk.Tk()
    app = RamseyGame(app_root)
    app_root.mainloop()
