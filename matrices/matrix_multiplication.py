# матрица 1
print("Ведите размер первой матрицы:")
n1, m1 = list(map(int, input().split(" ")))
matrix1 = []
for i in range(n1):
    matrix1.append([int(j) for j in input().split(" ")])

# матрица 2
print("Ведите размер второй матрицы:")
n2, m2 = list(map(int, input().split(" ")))
matrix2 = []
for i in range(n2):
    matrix2.append([int(j) for j in input().split(" ")])


final_matrix = [[0 for j in range(m2)] for i in range(n1)]


# Alkury - тг @alkury
def wibor(x1, y2, matrix1, matrix2):
    final_matrix0 = []
    k1 = matrix1[x1]
    k2 = [f[0] for f in [[matrix2[t][j] for j in range(len(matrix2[t])) if j == y2] for t in range(len(matrix2))]]
    for i in range(len(k1)):
        final_matrix0.append(k1[i] * k2[i])
    return final_matrix0


if m1 == n2:
    print("Матрица умножения:")
    for i in range(n1):
        for j in range(m2):
            final_matrix[i][j] = sum(wibor(i, j, matrix1, matrix2))
        print(*final_matrix[i])
else:
    print("Невозможно умножить матрицы. Размеры матриц не совпадают.")

