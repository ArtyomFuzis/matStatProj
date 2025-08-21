import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler


def robust_2sls(y, Z, endog_mask, X, alpha=0.5):
    """Улучшенная реализация 2SLS с правильным масштабированием"""
    # Конвертация данных
    y = np.asarray(y, dtype=np.float64).ravel()
    Z = np.asarray(Z, dtype=np.float64)
    X = np.asarray(X, dtype=np.float64)
    endog_mask = np.asarray(endog_mask)
    n, p = Z.shape

    # Масштабирование данных с сохранением константы
    y_scaler = StandardScaler()
    y_std = y_scaler.fit_transform(y.reshape(-1, 1)).flatten()

    # Масштабирование Z (исключая константу)
    Z_const = Z[:, [0]]  # Константный столбец
    Z_vars = Z[:, 1:]  # Остальные переменные

    if Z_vars.shape[1] > 0:
        Z_scaler = StandardScaler()
        Z_vars_std = Z_scaler.fit_transform(Z_vars)
        Z_std = np.hstack([Z_const, Z_vars_std])
    else:
        Z_std = Z_const.copy()
        Z_scaler = None

    # Масштабирование X (исключая константу)
    X_const = X[:, [0]]
    X_vars = X[:, 1:]

    if X_vars.shape[1] > 0:
        X_scaler = StandardScaler()
        X_vars_std = X_scaler.fit_transform(X_vars)
        X_std = np.hstack([X_const, X_vars_std])
    else:
        X_std = X_const.copy()
        X_scaler = None

    # Шаг 1: Прогнозирование эндогенных переменных
    Z_hat = Z_std.copy()

    if np.any(endog_mask) and X_scaler is not None:
        endog_indices = np.where(endog_mask)[0]

        for idx in endog_indices:
            # Пропускаем константу
            if idx == 0:
                continue

            endog_var = Z_std[:, idx]

            # Решение с регуляризацией
            try:
                XtX = X_std.T @ X_std
                XtX_reg = XtX + alpha * np.eye(XtX.shape[0])
                gamma = np.linalg.solve(XtX_reg, X_std.T @ endog_var)
                Z_hat[:, idx] = X_std @ gamma
            except:
                gamma = np.linalg.lstsq(X_std, endog_var, rcond=None)[0]
                Z_hat[:, idx] = X_std @ gamma

    # Шаг 2: Оценка уравнения с регуляризацией
    try:
        ZtZ = Z_hat.T @ Z_hat
        ZtZ_reg = ZtZ + alpha * np.eye(ZtZ.shape[0])
        beta_std = np.linalg.solve(ZtZ_reg, Z_hat.T @ y_std)
    except:
        beta_std = np.linalg.lstsq(Z_hat, y_std, rcond=None)[0]

    # Обратное масштабирование коэффициентов (без предупреждений)
    beta = np.zeros(p)

    # Извлекаем скалярные значения
    y_mean = y_scaler.mean_[0] if y_scaler.mean_.size > 1 else y_scaler.mean_
    y_scale = y_scaler.scale_[0] if y_scaler.scale_.size > 1 else y_scaler.scale_

    if Z_scaler is not None and Z_vars.shape[1] > 0:
        Z_means = Z_scaler.mean_
        Z_scales = Z_scaler.scale_

        # Расчет константы
        const_correction = 0
        for j in range(1, p):
            # Для каждого коэффициента переменной
            const_correction += beta_std[j] * Z_means[j - 1] * y_scale / Z_scales[j - 1]

        beta[0] = y_mean - const_correction

        # Коэффициенты переменных
        beta[1:] = beta_std[1:] * y_scale / Z_scales
    else:
        # Только константа
        beta[0] = y_mean

    return beta


def estimate_system(equations, X, use_log_transform=False):
    results = []
    for i, (y, Z, endog_mask) in enumerate(equations):
        try:
            # Подбираем коэффициент регуляризации
            best_alpha = 0
            best_r2 = -np.inf
            best_beta = None

            for alpha in [0.01, 0.1, 0.5, 1.0, 2.0]:
                beta = robust_2sls(y, Z, endog_mask, X, alpha=alpha)
                y_pred = Z @ beta
                ss_res = np.sum((y - y_pred) ** 2)
                ss_tot = np.sum((y - np.mean(y)) ** 2)
                r2 = 1 - (ss_res / ss_tot)

                if r2 > best_r2:
                    best_r2 = r2
                    best_alpha = alpha
                    best_beta = beta

            results.append((best_beta, best_alpha, best_r2))
            print(f"Уравнение {i + 1} оценено с alpha={best_alpha:.2f}, R²={best_r2:.4f}")
        except Exception as e:
            print(f"Ошибка в уравнении {i + 1}: {str(e)}")
            results.append((None, None, None))
    return results


# Test prog
if __name__ == "__main__":
    # Загрузка данных
    df = pd.read_excel("test2.xlsx", nrows=13, skiprows=21, usecols="K:S")
    n = df.shape[0]


    Z1 = np.column_stack([
        np.ones(n),
        df['Y(t-1)'],
        df['W(t)'],
        df['C(t)'],
        df['R(t)']
    ])

    Z2 = np.column_stack([
        np.ones(n),
        df['Y(t)'],
        df['K(t)']
    ])

    equations = [
        (df['Y(t)'], Z1, [True, False, False, True, False]),
        (df['C(t)'], Z2, [True, True, False])
    ]

    X_matrix = np.column_stack([
        np.ones(n),
        df['Y(t-1)']    ,
        df['R(t)'],
        df['K(t)'],
        df['W(t)']
    ])

    coefficients = estimate_system(equations, X_matrix, use_log_transform=False)
    print(coefficients)
    print("------------------------aaaaaaa------------------------")

    print('\n'.join(map(str, np.dot(Z1,coefficients[0][0]))))
    print("\n\n----------sep----------\n")
    print('\n'.join(map(str,np.dot(Z2,coefficients[1][0]))))