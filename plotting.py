import matplotlib.pyplot as plt

prey_population_data = []
predator_population_data = []

prey_avg_speed_data = []
predator_avg_speed_data = []
prey_max_speed_data = []
predator_max_speed_data = []
prey_min_speed_data = []
predator_min_speed_data = []

prey_avg_turning_rate = []
predator_avg_turning_rate = []
prey_max_turning_rate = []
predator_max_turning_rate = []
prey_min_turning_rate = []
predator_min_turning_rate = []

times = []

def record_time(time):
    times.append(time)

def gather_population_data(prey_population, predator_population):
    prey_population_data.append(prey_population)
    predator_population_data.append(predator_population)

def gather_speed_data(preys, predators):
    prey_speeds = [p.speed for p in preys]
    predator_speeds = [p.speed for p in predators]

    if prey_speeds:
        # Prey speed data
        prey_avg_speed_data.append(sum(prey_speeds) / len(prey_speeds))
        prey_max_speed_data.append(max(prey_speeds))
        prey_min_speed_data.append(min(prey_speeds))
    if predator_speeds:
        # Predator speed data
        predator_avg_speed_data.append(sum(predator_speeds) / len(predator_speeds))
        predator_max_speed_data.append(max(predator_speeds))
        predator_min_speed_data.append(min(predator_speeds))

def gather_turning_rate_data(preys, predators):
    prey_turning_rates = [p.turning_rate for p in preys]
    predator_turning_rates = [p.turning_rate for p in predators]

    if prey_turning_rates:
        prey_avg_turning_rate.append(sum(prey_turning_rates) / len(prey_turning_rates))
        prey_max_turning_rate.append(max(prey_turning_rates))
        prey_min_turning_rate.append(min(prey_turning_rates))
    if predator_turning_rates:
        predator_avg_turning_rate.append(sum(predator_turning_rates) / len(predator_turning_rates))
        predator_max_turning_rate.append(max(predator_turning_rates))
        predator_min_turning_rate.append(min(predator_turning_rates))

def plot_population_data():
    plt.plot(times, prey_population_data, label = 'Prey Population')
    plt.plot(times, predator_population_data, label = 'Predator Population')
    plt.legend()
    plt.xlabel("Time / seconds")
    plt.ylabel("Population")
    plt.title("Predator and Prey Populations against time")
    plt.show()

def plot_speed_data():
    t_prey = times[0:len(prey_avg_speed_data)]
    t_pred = times[0:len(predator_avg_speed_data)]

    # Plot average, min, and max lines
    plt.plot(t_prey, prey_avg_speed_data, label='Prey Speed', color='green')
    plt.plot(t_pred, predator_avg_speed_data, label='Predator Speed', color='red')
    plt.plot(t_prey, prey_max_speed_data, color='lightgreen')
    plt.plot(t_pred, predator_max_speed_data, color='pink')
    plt.plot(t_prey, prey_min_speed_data, color='lightgreen')
    plt.plot(t_pred, predator_min_speed_data, color='pink')

    # Shade between min and max for prey
    plt.fill_between(t_prey, prey_min_speed_data, prey_max_speed_data, color='green', alpha=0.15)
    # Shade between min and max for predator
    plt.fill_between(t_pred, predator_min_speed_data, predator_max_speed_data, color='red', alpha=0.15)

    plt.legend()
    plt.xlabel("Time / seconds")
    plt.ylabel("Speed")
    plt.title("Predator and Prey Speeds against time")
    plt.show()

def plot_turning_rate_data():
    t_prey = times[0:len(prey_avg_turning_rate)]
    t_pred = times[0:len(predator_avg_turning_rate)]

    # Plot average, min, and max lines for turning rates
    plt.plot(t_prey, prey_avg_turning_rate, label='Prey Turning Rate', color='green')
    plt.plot(t_pred, predator_avg_turning_rate, label='Predator Turning Rate', color='red')
    plt.plot(t_prey, prey_max_turning_rate, color='lightgreen')
    plt.plot(t_pred, predator_max_turning_rate, color='pink')
    plt.plot(t_prey, prey_min_turning_rate, color='lightgreen')
    plt.plot(t_pred, predator_min_turning_rate, color='pink')

    # Shade between min and max for prey turning rates
    plt.fill_between(t_prey, prey_min_turning_rate, prey_max_turning_rate, color='green', alpha=0.15)
    # Shade between min and max for predator turning rates
    plt.fill_between(t_pred, predator_min_turning_rate, predator_max_turning_rate, color='red', alpha=0.15)

    plt.legend()
    plt.xlabel("Time / seconds")
    plt.ylabel("Turning Rate")
    plt.title("Predator and Prey Turning Rates against time")
    plt.show()