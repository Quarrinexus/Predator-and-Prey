import matplotlib.pyplot as plt

prey_population_data = []
predator_population_data = []

prey_avg_speed_data = []
predator_avg_speed_data = []
prey_max_speed_data = []
predator_max_speed_data = []
prey_min_speed_data = []
predator_min_speed_data = []

times = []

def gather_population_data(prey_population, predator_population, time):
    times.append(time)
    prey_population_data.append(prey_population)
    predator_population_data.append(predator_population)

def gather_speed_data(preys, predators):
    prey_speeds = [p.speed for p in preys]
    predator_speeds = [p.speed for p in predators]

    if prey_speeds and predator_speeds:
        # Prey speed data
        prey_avg_speed_data.append(sum(prey_speeds) / len(prey_speeds))
        prey_max_speed_data.append(max(prey_speeds))
        prey_min_speed_data.append(min(prey_speeds))

        # Predator speed data
        predator_avg_speed_data.append(sum(predator_speeds) / len(predator_speeds))
        predator_max_speed_data.append(max(predator_speeds))
        predator_min_speed_data.append(min(predator_speeds))

def plot_population_data():
    plt.plot(times, prey_population_data, label = 'Prey Population')
    plt.plot(times, predator_population_data, label = 'Predator Population')
    plt.legend()
    plt.xlabel("Time / seconds")
    plt.ylabel("Population")
    plt.title("Predator and Prey Populations against time")
    plt.show()

def plot_speed_data():
    plt.plot(times[0:len(prey_avg_speed_data)], prey_avg_speed_data, label = 'Prey Average Speed')
    plt.plot(times[0:len(predator_avg_speed_data)], predator_avg_speed_data, label = 'Predator Average Speed')
    #plt.plot(times, prey_max_speed_data, label = 'Prey Max Speed')
    #plt.plot(times, predator_max_speed_data, label = 'Predator Max Speed')
    #plt.plot(times, prey_min_speed_data, label = 'Prey Min Speed')
    #plt.plot(times, predator_min_speed_data, label = 'Predator Min Speed')
    plt.legend()
    plt.xlabel("Time / seconds")
    plt.ylabel("Speed")
    plt.title("Predator and Prey Speeds against time")
    plt.show()