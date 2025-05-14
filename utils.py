import numpy as np
def shorten_string(string, n):
    if len(string) > n:
        return string[:n-3] + "..."
    return string

def calculate_msq(X, Y):
    matrix_X = np.hstack((np.ones((X.shape[0], 1)), X))
    matrix_Y = np.array(Y)
    # print("-----------------Xs-----------------")
    # print(matrix_X)
    # print("-----------------Ys-----------------")
    # print(matrix_Y)
    # print("-----------------RESULTS-----------------")
    res = np.dot(np.dot(np.linalg.inv(np.dot(matrix_X.T, matrix_X)), matrix_X.T), matrix_Y)
    # print(res)
    return res


