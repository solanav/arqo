from dataclasses import dataclass

branch = [
    "beq",
    "bnq",
]

lw = [
    "lw",
    "load",
    "st",
    "ld"
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
    id: int
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

    nu_pins = []
    id = 1
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
            cleani = i[2].replace(")", "").split("(")[-1]
            reads_from.append(cleani)

        # Si la instruccion es de tipo store
        elif i[0] in lw:
            reads_from.append(i[1])
            cleani = i[2].replace(")", "").split("(")[-1]
            writes_to.append(cleani)

        # Si la instruccion es de tipo branch
        elif i[0] in branch:
            reads_from.append(i[1])
            reads_from.append(i[2])

        nu_pins.append(Instruction(id, i[0], writes_to, reads_from))
        id += 1

    return nu_pins


def find_hazards(fname, von_neuman=True):
    instructions = parse_ins(fname)

    for curr_ins in instructions:
        for re_ins in instructions:
            if re_ins == curr_ins:
                break

            # Check RAW
            for w in curr_ins.reads_from:
                if w in re_ins.writes_to:
                    print("RAW hazard, I{} con I{} por {}".format(
                        curr_ins.id,
                        re_ins.id,
                        w.upper()
                    ))

            # Check WAR
            for w in curr_ins.writes_to:
                if w in re_ins.reads_from:
                    print("WAR hazard, I{} con I{} por {}".format(
                        curr_ins.id,
                        re_ins.id,
                        w.upper()
                    ))

            # Check WAW
            for w in curr_ins.writes_to:
                if w in re_ins.writes_to:
                    print("WAW hazard, I{} con I{} por {}".format(
                        curr_ins.id,
                        re_ins.id,
                        w.upper()
                    ))

def main():
    find_hazards("data.asm", von_neuman=True)


if __name__ == "__main__":
    main()