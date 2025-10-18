from simulation import Simulation
from gui import Brain_GUI
from plotting import RealTimePlotter
import multiprocessing as mp
from sys import exit

def main():
    brain_queue = mp.Queue()
    population_queue = mp.Queue()
    simulation = Simulation(brain_queue, population_queue, new_simulation=True)
    side_gui = Brain_GUI(brain_queue)
    plotter = RealTimePlotter(population_queue)
    simulation.start()
    side_gui.start()
    plotter.start()
    simulation.join()
    side_gui.join()
    plotter.join()
    brain_queue.close()
    population_queue.close()
    exit()

if __name__ == "__main__":
    main()