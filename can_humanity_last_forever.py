a = 5/6
r = 0.8
print(a**(1/(1-r)))
for century in range(21, 101):
    print(f"{century} {a:.2f}, {1-a}")
    a = a**r


