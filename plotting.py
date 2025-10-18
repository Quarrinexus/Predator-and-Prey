import multiprocessing as mp
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt

class RealTimePlotter(mp.Process):
    def __init__(self, data_queue):
        super().__init__()
        self.data_queue = data_queue # corresponds to population_queue in main.py

        # Enable interactive mode so updates appear without blocking
        plt.ion()

        # Storage for times and population series
        self.prey_population_data = []
        self.predator_population_data = []
        self.times = []

        # Create figure and axes (note: creating GUI objects here may initialize GUI in parent process)
        self.fig, self.ax = plt.subplots()
        # Set the window title via the canvas manager (cross-backend)
        self.fig.canvas.manager.set_window_title('Real-Time Population Plotter')
        # Create empty lines for prey and predator that will be updated
        self.line1, = self.ax.plot([], [], label='Prey Population')
        self.line2, = self.ax.plot([], [], label='Predator Population')
        # Set initial axis limits and labels
        self.ax.set_xlim(0, 10)
        self.ax.set_ylim(0, 100)
        self.ax.set_xlabel("Time / seconds")
        self.ax.set_ylabel("Population")
        self.ax.set_title("Predator and Prey Populations against Time")
        self.ax.legend()


    def update_plot(self, frame=None):
        if len(self.times) > 0:
            # update line data
            self.line1.set_data(self.times, self.prey_population_data)
            self.line2.set_data(self.times, self.predator_population_data)
            # extend x-axis slightly past last time point
            self.ax.set_xlim(0, max(self.times) + 1)
            # set y-axis to fit max population + margin
            max_population = max(max(self.prey_population_data), max(self.predator_population_data))
            self.ax.set_ylim(0, max_population + 10)
            # recompute limits and redraw efficiently
            self.ax.relim()
            self.ax.autoscale_view()
            self.fig.canvas.draw_idle()

    def record_time(self, time):
        # Append a new time value used as the x-axis
        self.times.append(time)

    def gather_population_data(self, prey_population, predator_population):
        # Append latest population counts to respective series
        self.prey_population_data.append(prey_population)
        self.predator_population_data.append(predator_population)

    def run(self):
        running = True
        while running:
            if not self.data_queue.empty():
                time, prey_population, predator_population = self.data_queue.get()
                # Quit signal handling
                if time == "QUIT":
                    running = False
                    break
                # Store and visualize new data point
                self.record_time(time)
                self.gather_population_data(prey_population, predator_population)
                self.update_plot()
                # Allow GUI event loop to process events and show updates
                plt.pause(0.5)
            
        # Close the figure to free resources
        plt.close(self.fig)