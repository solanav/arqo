from dataclasses import dataclass

EMPTY = "-"

branch = ["beq", "bnq"]
lw = ["lw", "load", "st", "ld"]
sw = ["sw", ]
rtype = ["add", "sub", "and", "or", "slt", "nor"]


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


@dataclass
class Pipeline:
    name: str
    blocked: bool
    ins: int


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

        instruction_name = i[0]

        # Si la instruccion es de tipo r
        if instruction_name in rtype:
            writes_to.append(i[1])
            reads_from.append(i[2])
            reads_from.append(i[3])

        # Si la instruccion es de tipo load
        elif instruction_name in lw:
            writes_to.append(i[1])
            cleani = i[2].replace(")", EMPTY).split("(")[-1]
            reads_from.append(cleani)

        # Si la instruccion es de tipo store
        elif instruction_name in sw:
            reads_from.append(i[1])
            cleani = i[2].replace(")", EMPTY).split("(")[-1]
            writes_to.append(cleani)

        # Si la instruccion es de tipo branch
        elif instruction_name in branch:
            reads_from.append(i[1])
            reads_from.append(i[2])

        nu_pins.append(Instruction(id, i[0], writes_to, reads_from))
        id += 1

    return nu_pins


def print_riesgos(title, riesgos):
    for r1, r2, w in riesgos:
        print("{} hazard, {} con {} por {}".format(
            title,
            r1,
            r2,
            w.upper()
        ))


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
                    raw.append((curr_ins, re_ins, w))

            # Check WAR
            for w in curr_ins.writes_to:
                if w in re_ins.reads_from:
                    war.append((curr_ins, re_ins, w))

            # Check WAW
            for w in curr_ins.writes_to:
                if w in re_ins.writes_to:
                    waw.append((curr_ins, re_ins, w))

    return raw, war, waw


def execute_table(ins, raw, war, waw):
    print("[Clock] [  IF   |  ID   |  EX   |  MEM  |  WB   ]")

    p_if = Pipeline("if", False, EMPTY)
    p_id = Pipeline("id", False, EMPTY)
    p_ex = Pipeline("ex", False, EMPTY)
    p_mem = Pipeline("mem", False, EMPTY)
    p_wb = Pipeline("wb", False, EMPTY)

    executed = []

    # Start executing the program
    curr_ins = 0
    clock = 1
    while True:
        # Unblock everything
        p_if.blocked = False
        p_id.blocked = False
        p_ex.blocked = False
        p_mem.blocked = False
        p_wb.blocked = False

        # Check if we need to stop shit because of RAW
        if p_id.ins != EMPTY:
            # Comprobamos los riesgos
            for x, y, _ in raw:
                # Comprobamos que el riesgo nos incluye
                if x.id != p_id.ins.id:
                    continue

                # Comprobamos que la instruccion es anterior
                if x.id <= y.id:
                    continue

                # Comprobamos que no se haya ejecutado ya
                ejecutada = False
                for e in executed:
                    # Si ya la hemos ejecutado, no pacha nada
                    if y.id == e.id:
                        ejecutada = True
                if ejecutada:
                    continue

                # Si no se ha cumplido ninguna de las comprobaciones, bloqueamos
                p_ex.blocked = True
                break

        # Move wb to executed
        if p_wb.ins != EMPTY:
            executed.append(p_wb.ins)
            p_wb.ins = EMPTY

            # If last instructionn has been executed, exit
            last_instruction = ins[-1]
            for e in executed:
                if last_instruction.id == e.id:
                    return

        # Movemos las instrucciones que no esten bloqueadas
        if not p_wb.blocked and p_wb.ins == EMPTY:
            p_wb.ins = p_mem.ins
            p_mem.ins = EMPTY
        if not p_mem.blocked and p_mem.ins == EMPTY:
            p_mem.ins = p_ex.ins
            p_ex.ins = EMPTY
        if not p_ex.blocked and p_ex.ins == EMPTY:
            p_ex.ins = p_id.ins
            p_id.ins = EMPTY
        if not p_id.blocked and p_id.ins == EMPTY:
            p_id.ins = p_if.ins
            p_if.ins = EMPTY

        # Load the new instruction
        if not p_if.blocked and p_if.ins == EMPTY:
            try:
                p_if.ins = ins[curr_ins]
                curr_ins += 1
            except:
                p_if.ins = EMPTY

        print("[{: ^5}] [{: ^7}|{: ^7}|{: ^7}|{: ^7}|{: ^7}]".format(
            clock,
            p_if.ins,
            p_id.ins,
            p_ex.ins,
            p_mem.ins,
            p_wb.ins,
        ))

        clock += 1

        if curr_ins >= 50:
            return


def main():
    instructions = parse_ins("data.asm")

    raw, war, waw = find_hazards(instructions)
    print("\n\n{:=<40}\n".format("RIESGOS"))
    print_riesgos("RAW", raw)
    print_riesgos("WAR", war)
    print_riesgos("WAW", waw)


    print("\n\n{:=<40}\n".format("EJECUCION"))
    execute_table(instructions, raw, war, waw)


if __name__ == "__main__":
    main()
