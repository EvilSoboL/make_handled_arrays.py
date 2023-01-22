import numpy as np
import pathlib
from pathlib import Path
import os


def handled_arrays(path_with_mode):
    """
    Функция принимает путь к одному режиму, обрабатывает его и создает папку с именем режима, где у
    :param path_with_mode:
    :return: None
    """
    # Загрузка массива одного из режима
    path_to_unhandled_array = Path("modes", "{}".format(path_with_mode))
    unhandled_array = np.loadtxt(path_to_unhandled_array, skiprows=1, usecols=(range(2, 14)))

    # Создание массивов для дальнейшего присвоения туда обработанного массива
    array_out_mean = np.array(range(unhandled_array.shape[1])).reshape(1, 12)
    array_out_sko = array_out_mean
    # Основной алгоритм создания обработанного массива
    i = 0
    while i < unhandled_array.shape[0]:
        if unhandled_array[i][1] < 18:  # Поиск по массиву значений О2 < 18%
            time_start = unhandled_array[i][0]  # Запись времени начала среза 70 секунд
            index_start = i  # Индекс начала массива
            # Алгоритм создания срезов массива по 70 секунд
            # Длительность среза массива (время выхода на стационар + измерения)
            with open("config.txt") as config:
                rows_in_config = 0
                for row in config:
                    for symbols in range(len(row)):
                        if row[symbols] == ":":
                            if rows_in_config == 0:
                                slice_duration = float(row[symbols + 1:])
                            elif rows_in_config == 1:
                                averaging_duration = float(row[symbols + 1:])
                            rows_in_config += 1
            # Прибавляем i до тех пор пока значение времени не будет + 70 секунд
            while time_start + slice_duration > unhandled_array[i][0] and i != (unhandled_array.shape[0] - 1):
                i += 1
            index_stop = i  # Записываем индекс после +70 секунд
            array_slice = unhandled_array[index_start:index_stop]  # Создание среза 70 секунд
            if np.any(array_slice[:, 1] > 20):  # Поиск в массиве значений > 20
                # Если в срезе
                while unhandled_array[i][1] < 20 and i != (unhandled_array.shape[0] - 1):
                    i += 1
            else:
                counter = -1
                # Длительность периода измерения
                # Алгоритм, который считает мат. ожидание, СКО последних 20 секунд замера 70 секунд
                while array_slice[-1][0] - averaging_duration < array_slice[counter][0]:
                    counter -= 1
                array_slice_begin = counter
                array_slice_mean_20 = np.mean(array_slice[array_slice_begin:index_stop], axis=0).reshape(1, 12)
                array_slice_sko_20 = np.std(array_slice[array_slice_begin:index_stop], axis=0).reshape(1, 12)
                array_slice_mean_20[0][0] = time_start
                array_out_mean = np.append(array_out_mean, array_slice_mean_20, axis=0)
                array_out_sko = np.append(array_out_sko, array_slice_sko_20, axis=0)
                # Алгоритм поиска элементов массива, которые соответсвуют концу обдувки газоанализатора
                while unhandled_array[i][1] < 20 and i != (unhandled_array.shape[0] - 1):
                    i += 1
        i += 1

        def convert_to_txt(array_out_mean, array_out_sko, path_with_mode):
            """
            Функция обрабатывает, полученные массивы: добавление заголовков столбцов, цисловое форматирование, оси
            газоанализатора. Сохраняет массивы в файл txt в папку с названием режима
            :return: None
            """
            # Удаление первых (вспомогательных) строк массивов
            array_out_mean = np.delete(array_out_mean, 0, axis=0)
            array_out_sko = np.delete(array_out_sko, 0, axis=0)

            # Добавление вспомогательного первого столбца для оси газоанализатора
            supporting_table = np.array(range(len(array_out_mean))).reshape(len(array_out_mean), 1)
            # Создание массива единиц, чтобы при нахождении процентов получилось корректное отображение времени
            supporting_table_sko = np.ones((array_out_mean.shape[0], 1))
            array_out_mean = np.concatenate([supporting_table, array_out_mean], axis=1)
            array_out_sko = np.concatenate([supporting_table_sko, array_out_sko], axis=1)
            # Вывод массива с мат. ожиданием и процентами в одном массиве
            array_procent = (array_out_sko/array_out_mean) * 100
            # Пустой массив для создания нового массива: мат.ожидание - проценты
            array_mean_procent = np.array(range(array_procent.shape[0])).reshape(array_procent.shape[0], 1)
            for x in range(1, array_out_mean.shape[1]):
                array_mean_procent = np.append(array_mean_procent,
                                               np.hstack([array_out_mean[:, x].reshape(array_procent.shape[0], 1),
                                                          array_procent[:, x].reshape(array_procent.shape[0], 1)]),
                                               axis=1)

            # Оформление таблиц
            fmt = "%d ", "%d", "%1.3f ", "%1.3f ", "%1.3f ", "%1.3f ", "%1.3f ", "%1.3f ", "%1.3f ", "%1.3f ",\
                  "%1.3f ", "%1.3f ", "%1.3f "
            header = "-(mm) sec " "O2(%) " "H2(%) " "CO(%) " "CO2(%) " "CH4(%) " "SO2(ppm) " "NO(ppm) " "NO2(ppm) "\
                     "N2O(ppm) " "t(oC) " "P(mm.pt.st.)"
            header_procent = "-(mm)  sec              " "O2(%)          " "H2(%)          " "CO(%)          " \
                             "CO2(%)          " "CH4(%)          " "SO2(ppm)          " "NO(ppm)          " \
                             "NO2(ppm)          " "N2O(ppm)          " "t(oC)         " "P(mm.pt.st.)"
            # Добавление оси хода газоанализатора
            step_gas_analyzer = 200
            for k in range(len(array_out_mean)):
                array_out_mean[k][0] = step_gas_analyzer
                array_out_sko[k][0] = step_gas_analyzer
                array_mean_procent[k][0] = step_gas_analyzer
                step_gas_analyzer -= 20
                if step_gas_analyzer < 20:
                    step_gas_analyzer = 200

            if os.path.exists("{}_dir".format(path_with_mode[:-4])):
                path_to_save = Path("{}_dir".format(path_with_mode[:-4]), "{}".format(path_with_mode[:-4]))
                np.savetxt(path_to_save, array_out_mean, fmt=fmt, header=header)

                path_to_save_sko = Path("{}_dir".format(path_with_mode[:-4]), "{}_SKO".format(path_with_mode[:-4]))
                np.savetxt(path_to_save_sko, array_out_sko, fmt=fmt, header=header)

                path_to_save_procent = Path("{}_dir".format(path_with_mode[:-4]), "{}_procent".format(path_with_mode[:-4]))
                np.savetxt(path_to_save_procent, array_mean_procent, fmt="% 1.3f", header=header_procent)
            else:
                os.makedirs("{}_dir".format(path_with_mode[:-4]))
                path_to_save = Path("{}_dir".format(path_with_mode[:-4]), "{}".format(path_with_mode[:-4]))
                np.savetxt(path_to_save, array_out_mean, fmt=fmt, header=header)

                path_to_save_sko = Path("{}_dir".format(path_with_mode[:-4]), "{}_SKO".format(path_with_mode[:-4]))
                np.savetxt(path_to_save_sko, array_out_sko, fmt=fmt, header=header)

                path_to_save_procent = Path("{}_dir".format(path_with_mode[:-4]), "{}_procent".format(path_with_mode[:-4]))
                np.savetxt(path_to_save_procent, array_mean_procent, fmt="% 1.3f", header=header_procent)

    convert_to_txt(array_out_mean, array_out_sko, path_with_mode)


def measurement_modes(path_with_modes):
    """
    Функция, получая путь к папке с режимами, поочередно вызывает функцию обработки массива для каждого из режима.
    :param path_with_modes: путь к папке с txt файлами с измерениями.
    :return: None
    """
    modes_list = os.listdir(path_with_modes)
    for modes in range(len(modes_list)):
        handled_arrays(modes_list[modes])


measurement_modes("modes")
