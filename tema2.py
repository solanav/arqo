from dataclasses import dataclass

branch = [
    "beq",
    "bnq",
    "jump",
    "jp",
]

lw = [
    "lw",
    "load",
    "st",
]

sq = [
    "sw",
]

rtype = [
    "add",
    "sub",
    "and",
    "or",
    "slt",
    "nor",
]

@dataclass
class Instruction:
    name: str
    writes_to: []
    reads_from: []

def parse_ins(fname):
    instructions = open(fname).read().split("\n")

    pins = []
    for i in instructions:
        s = i.replace(",", "").split()
        nus = []
        for part in s:
            nus.append(part.lower())
        pins.append(nus)

    for i in pins:
        writes_to = []
        reads_from = []

        # Si la instruccion es de tipo r
        if i[0] in rtype:
            writes_to.append(i[1])
            reads_from.append(i[2])
            reads_from.append(i[3])

        # Si la instruccion es de tipo load
        elif i[0] in lw:
            writes_to.append(i[1])
            cleani = i.replace(")", "").split("(")[-1]
            reads_from.append(cleani)

        # Si la instruccion es de tipo store
        elif i[0] in lw:
            reads_from.append(i[1])
            cleani = i.replace(")", "").split("(")[-1]
            writes_to.append(cleani)

        # Si la instruccion es de tipo salto
        # No escribimos ni mierdas

        pins.append(Instruction(i[0], writes_to, reads_from))


    return pins


def find_hazards(fname, von_neuman=True):
    instructions = parse_ins(fname)

    raw = []
    war = []
    waw = []

    for curr_ins in instructions:
        print("Checking {}".format(curr_ins[0]))

        for re_ins in instructions:
            if re_ins == curr_ins:
                break

            print("\tChecking with {}".format(re_ins[0]))


def main():
    find_hazards("data.asm", von_neuman=True)


if __name__ == "__main__":
    main()