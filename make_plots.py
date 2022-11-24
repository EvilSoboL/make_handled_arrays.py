import os
import matplotlib.pyplot as plt
import numpy as np


def make_plots():
    """
    Функция по обработанным массивам строит общий график компонента по всем режимам
    :return: None
    """
    # Поиск папок с обработанными данными
    list_full_dir = os.listdir()
    list_modes = list()
    for n in range(len(list_full_dir)):
        if list_full_dir[n][-3:] == "dir":
            list_modes.append(list_full_dir[n])

    list_components = [" ", "time", "O2", "H2", "СO", "СO2", "СH4", "SO2", "NO", "NO2", "N2O", "t", "P"]
    for current_element in range(2, len(list_components)):
        for n in range(len(list_modes)):
            data_to_plot = np.loadtxt("{}\\{}".format(list_modes[n], list_modes[n][:-4]))
            plt.plot(data_to_plot[:, 0], data_to_plot[:, current_element], label="{}".format(list_modes[n][:-4]))
            plt.grid()
            plt.xlabel("mm")
            # Выносим легенду за график
            plt.legend(loc="upper center", bbox_to_anchor=(0.5, 1.15), ncol=3)
            if current_element < 7:
                plt.ylabel("vol.%")
            elif current_element == 11:
                plt.ylabel("Celsius")
            elif current_element == 12:
                plt.ylabel("mmHg")
            else:
                plt.ylabel("ppm")
        if os.path.exists("plot"):
            plt.savefig("plot\\{}".format(list_components[current_element]))
            plt.clf()
        else:
            os.makedirs("plot")
            plt.savefig("plot\\{}".format(list_components[current_element]))
            plt.clf()


make_plots()
