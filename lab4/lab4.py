import pandas as pd
import numpy as np
from numpy import random
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score


# x - время
# y - очки

def forecast(test, train, file_to_continue):
    df_new_csv = pd.read_csv(file_to_continue)
    df_test = pd.read_csv(test)
    df_train = pd.read_csv(train)
    y_train = df_train['Points'].tolist()
    x_train = list()
    times_train = df_train['GameTime'].tolist()
    x_test_values = list()
    y_test_values = df_test['Points'].tolist()
    times_test = df_test['GameTime'].tolist()
    for time in times_train:
        x_train.append(float(time.replace("0:00:", "")))
    for time in times_test:
        x_test_values.append(float(time.replace("0:00:", "")))
    x_test = np.array(x_test_values).reshape((-1, 1))
    x_train = np.array(x_train).reshape((-1, 1))
    model = LinearRegression()
    model.fit(x_train, y_train)
    test = model.predict(x_test)
    print("Score R2:" + str(r2_score(y_test_values, test)))
    min_value_x = df_test['GameTime'].min()
    max_value_x = df_test['GameTime'].max()
    min_value_x = float(min_value_x.replace("0:00:", ""))
    max_value_x = float(max_value_x.replace("0:00:", ""))
    random_times = list()
    for i in range(10):
        random_time = round(random.uniform(max_value_x, min_value_x), 6)
        random_times.append(random_time)
    random_times_array = np.array(random_times).reshape((-1, 1))
    predicts = model.predict(random_times_array).tolist()
    for i in range(len(predicts)):
        is_win = True
        if predicts[i] < 900:
            is_win = False
        print("{},{},{},{}".format(df_test.values[0][0],
                                   is_win, "0:00:" + str(random_times[i]), int(predicts[i])))
        entity = pd.DataFrame({"AlgorithmAgent": [df_test.values[0][0]],
                               "IsWon": [is_win],
                               "GameTime": ["0:00:" + str(random_times[i])],
                               "Points": [int(predicts[i])]})
        df_new_csv = df_new_csv.append(entity)
    df_new_csv.to_csv('stats_new.csv', index=False)


def main():
    forecast(r'stats_expectimax_test.csv', r'stats_expectimax_train.csv', r'stats.csv')
    forecast(r'stats_alphabeta_test.csv', r'stats_alphabeta_train.csv', r'stats_new.csv')


if __name__ == "__main__":
    main()
