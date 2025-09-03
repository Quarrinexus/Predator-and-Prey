import matplotlib.pyplot as plt

prey_population_data = []
predator_population_data = []

times = []

def record_time(time):
    times.append(time)

def gather_population_data(prey_population, predator_population):
    prey_population_data.append(prey_population)
    predator_population_data.append(predator_population)

def plot_population_data():
    plt.plot(times, prey_population_data, label = 'Prey Population')
    plt.plot(times, predator_population_data, label = 'Predator Population')
    plt.legend()
    plt.xlabel("Time / seconds")
    plt.ylabel("Population")
    plt.title("Predator and Prey Populations against time")
    plt.show()