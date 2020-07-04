
def tiempo_cpu(numero_ins, clocks_por_ins, tiempo_ciclo):
    return numero_ins * clocks_por_ins * tiempo_ciclo


def mejora(tiempo_x, tiempo_y):
    return tiempo_y / tiempo_x


def mips(numero_ins, tiempo):
    return numero_ins / (tiempo * 1000000)


def mflops(numero_ins_fp, tiempo):
    return mips(numero_ins_fp, tiempo)


def amdahl(enhancement_tuples):
    mejora = []
    no_mejora = []
    done = []

    # Distinguimos si mejora o no
    for e in enhancement_tuples:
        nombre, porcentaje, bef, aft = e
        if bef == aft:
            no_mejora.append(e)
        else:
            mejora.append(e)

    # Por cada instrucion
    ag = 0
    for e in mejora:
        nombre, porcentaje, bef, aft = e
        am = bef/aft

        tot = 0
        print("\t")
        for e in enhancement_tuples:
            nombre2, porcentaje2, bef2, aft2 = e
            if nombre2 in done:
                print("({} * {}) + ".format(porcentaje2, aft2), end='')
                tot += porcentaje2 * aft2
            else:
                print("({} * {}) + ".format(porcentaje2, bef2), end='')
                tot += porcentaje2 * bef2
        print()

        fm = (porcentaje * bef) / tot

        agtmp = 1 / ((1-fm) + (fm/am))
        ag += agtmp

        print("{}, AG={:f}, FM={:f}, AM={:f}".format(nombre, agtmp, fm, am))

        done.append(nombre)

    return ag


def main():
    speedup = amdahl([
        ("SCF", 15/100, 40, 2),
        ("MCF", 10/100, 60, 15),
        ("DCF", 5/100, 100, 10),
        ("INT", 70/100, 2, 2)])

    print(speedup)


if __name__ == "__main__":
    main()