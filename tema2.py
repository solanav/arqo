from dataclasses import dataclass

EMPTY = "-"

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

    def __str__(self):
        return "I{}".format(self.id)

    def __format__(self, format_spec):
        return str(self).__format__(format_spec)


def parse_ins(fname):
    instructions = open(fname).read().split("\n")

    pins = []
    for i in instructions:
        s = i.replace(",", EMPTY).split()
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
            cleani = i[2].replace(")", EMPTY).split("(")[-1]
            reads_from.append(cleani)

        # Si la instruccion es de tipo store
        elif i[0] in lw:
            reads_from.append(i[1])
            cleani = i[2].replace(")", EMPTY).split("(")[-1]
            writes_to.append(cleani)

        # Si la instruccion es de tipo branch
        elif i[0] in branch:
            reads_from.append(i[1])
            reads_from.append(i[2])

        nu_pins.append(Instruction(id, i[0], writes_to, reads_from))
        id += 1

    return nu_pins


def find_hazards(instructions):
    raw = []
    war = []
    waw = []

    for curr_ins in instructions:
        for re_ins in instructions:
            if re_ins == curr_ins:
                break

            # Check RAW
            for w in curr_ins.reads_from:
                if w in re_ins.writes_to:
                    raw.append((curr_ins, re_ins))
                    print("RAW hazard, I{} con I{} por {}".format(
                        curr_ins.id,
                        re_ins.id,
                        w.upper()
                    ))

            # Check WAR
            for w in curr_ins.writes_to:
                if w in re_ins.reads_from:
                    war.append((curr_ins, re_ins))
                    print("WAR hazard, I{} con I{} por {}".format(
                        curr_ins.id,
                        re_ins.id,
                        w.upper()
                    ))

            # Check WAW
            for w in curr_ins.writes_to:
                if w in re_ins.writes_to:
                    waw.append((curr_ins, re_ins))
                    print("WAW hazard, I{} con I{} por {}".format(
                        curr_ins.id,
                        re_ins.id,
                        w.upper()
                    ))

    return raw, war, waw


def execute_table(ins, raw, war, waw):
    print("[Clock] [  IF   |  ID   |  EX   |  MEM  |  WB   ]")

    curr_if = EMPTY
    curr_id = EMPTY
    curr_ex = EMPTY
    curr_mem = EMPTY
    curr_wb = EMPTY

    executed = []

    # Start executing the program
    curr_ins = 1
    while True:
        for e in executed:
            if ins[-1].id == e.id:
                return

        # Unblock everything
        block_if = False
        block_id = False
        block_ex = False
        block_mem = False
        block_wb = False

        # Check if we need to stop shit because of RAW
        if curr_id != EMPTY:
            # Comprobamos los riesgos
            for x, y in raw:
                # No nos afecta? Volvemos
                if x.id != curr_id.id:
                    continue

                # Es una instruccion anterior, nada
                if x.id <= y.id:
                    continue

                # No la hemos ejecutado
                ejecutada = False
                for e in executed:
                    # Si ya la hemos ejecutado, no pacha nada
                    if y.id == e.id:
                        ejecutada = True

                if ejecutada:
                    continue

                block_ex = True
                break

        # Move wb to executed
        if curr_wb != EMPTY:
            executed.append(curr_wb)
            curr_wb = EMPTY

        # Move if not blocked
        if not block_wb and curr_wb == EMPTY:
            curr_wb = curr_mem
            curr_mem = EMPTY
        if not block_mem and curr_mem == EMPTY:
            curr_mem = curr_ex
            curr_ex = EMPTY
        if not block_ex and curr_ex == EMPTY:
            curr_ex = curr_id
            curr_id = EMPTY
        if not block_id and curr_id == EMPTY:
            curr_id = curr_if
            curr_if = EMPTY

        # Load the new instruction
        if not block_if and curr_if == EMPTY:
            try:
                curr_if = ins[curr_ins - 1]
                curr_ins += 1
            except:
                curr_if = EMPTY

        print("[{: ^5}] [{: ^7}|{: ^7}|{: ^7}|{: ^7}|{: ^7}]".format(
            curr_ins,
            curr_if,
            curr_id,
            curr_ex,
            curr_mem,
            curr_wb,
        ))

        if curr_ins >= 50:
            return


def main():
    instructions = parse_ins("data.asm")

    print("\n\n{:=<40}\n".format("RIESGOS"))
    raw, war, waw = find_hazards(instructions)

    print("\n\n{:=<40}\n".format("EJECUCION"))
    execute_table(instructions, raw, war, waw)


if __name__ == "__main__":
    main()
