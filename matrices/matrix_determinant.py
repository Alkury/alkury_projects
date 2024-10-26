def determinant(d):
    g = []
    for i in range(len(d[0])):
        sum_di = 0
        for j in range(len(d)):
            sum_di += d[(i + j) % len(d[0])][j]
        g.append(sum_di)
    A = sum([g[k] * (-1) ** k for k in range(len(g))])
    return A


print("Ведите размер матрицы:")
n, m = list(map(int, input().split(" ")))
d = []
for i in range(n):
    d.append([int(j) for j in input().split(" ")])
