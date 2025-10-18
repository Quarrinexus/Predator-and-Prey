import multiprocessing as mp
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt

class RealTimePlotter(mp.Process):
    def __init__(self, data_queue):
        super().__init__()
        self.data_queue = data_queue

        plt.ion()

        self.prey_population_data = []
        self.predator_population_data = []
        self.times = []

        self.fig, self.ax = plt.subplots()
        self.fig.canvas.manager.set_window_title('Real-Time Population Plotter')
        self.line1, = self.ax.plot([], [], label='Prey Population')
        self.line2, = self.ax.plot([], [], label='Predator Population')
        self.ax.set_xlim(0, 10)
        self.ax.set_ylim(0, 100)
        self.ax.set_xlabel("Time / seconds")
        self.ax.set_ylabel("Population")
        self.ax.set_title("Predator and Prey Populations against time")
        self.ax.legend()


    def update_plot(self, frame=None):
        if len(self.times) > 0:
            self.line1.set_data(self.times, self.prey_population_data)
            self.line2.set_data(self.times, self.predator_population_data)
            
            self.ax.set_xlim(0, max(self.times) + 1)
            max_population = max(max(self.prey_population_data), max(self.predator_population_data))
            self.ax.set_ylim(0, max_population + 10)
            self.ax.relim()
            self.ax.autoscale_view()

            self.fig.canvas.draw_idle()

    def record_time(self, time):
        self.times.append(time)

    def gather_population_data(self, prey_population, predator_population):
        self.prey_population_data.append(prey_population)
        self.predator_population_data.append(predator_population)

    def run(self):
        running = True
        while running:
            if not self.data_queue.empty():
                time, prey_population, predator_population = self.data_queue.get()
                if time == "QUIT":
                    running = False
                    break
                self.record_time(time)
                self.gather_population_data(prey_population, predator_population)
                self.update_plot()
                plt.pause(0.5)
            
        plt.close(self.fig)

if __name__ == "__main__":
    plotter = RealTimePlotter(mp.Queue())
    plotter.start()
    plotter.join()
    exit()