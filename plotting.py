import matplotlib.pyplot as plt

def plot_population_data(prey_population_data, predator_population_data, time):
    plt.plot(time, prey_population_data, label = 'Prey Population')
    plt.plot(time, predator_population_data, label = 'Predator Population')
    plt.legend()
    plt.xlabel("Time / seconds")
    plt.ylabel("Population")
    plt.title("Predator and Prey Populations against time")
    plt.show()