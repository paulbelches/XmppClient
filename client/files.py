
of = open("Netflix.jpg", "rb")
lines = of.read()
print(lines)
ff = open("Netflix2.jpg", "xb")
ff.write(lines)
ff.close()