from dataclasses import dataclass
from enum import Enum

EMPTY = "-"

branch = ["beq", "bnq"]
lw = ["lw", "load", "st", "ld"]
sw = ["sw", "store"]
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


class PipeFunc(Enum):
    RR = 0 # We read registers here
    WR = 1 # We write registers here
    LI = 2 # We load instructions here
    ZZ = 3 # We don't do shit


@dataclass
class Pipeline:
    name: str
    blocked: bool
    ins: int
    function: PipeFunc


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

        instruction_name = i[0]

        # Si la instruccion es de tipo r
        if instruction_name in rtype:
            writes_to.append(i[1])
            reads_from.append(i[2])
            reads_from.append(i[3])

        # Si la instruccion es de tipo load
        elif instruction_name in lw:
            writes_to.append(i[1])
            cleani = i[2].replace(")", "").split("(")[-1]
            reads_from.append(cleani)

        # Si la instruccion es de tipo store
        elif instruction_name in sw:
            reads_from.append(i[1])
            cleani = i[2].replace(")", "").split("(")[-1]
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



def get_rr(pipes):
    for i, p in enumerate(pipes):
        if p.function == PipeFunc.RR:
            return i


def get_wr(pipes):
    for i, p in enumerate(pipes):
        if p.function == PipeFunc.WR:
            return i


def get_li(pipes):
    for i, p in enumerate(pipes):
        if p.function == PipeFunc.LI:
            return i


def print_pipes(pipes, clock):
    print("[{: ^5}] |".format(clock), end="")
    for p in pipes:
        print("{: ^7}|".format(p.ins), end="")
    print()


def execute_table(ins, raw, pipes):
    print("[Clock] |", end="")
    for p in pipes:
        print("{: ^7}|".format(p.name.upper()), end="")
    print()

    executed = []

    # Start executing the program
    curr_ins = 0
    clock = 1
    while True:
        # Unblock everything
        for i in range(len(pipes)):
            pipes[i].blocked = False

        # Check if we need to stop shit because of RAW
        rr_pipe = get_rr(pipes)
        if pipes[rr_pipe].ins != EMPTY:
            # Comprobamos los riesgos
            for x, y, _ in raw:
                # Comprobamos que el riesgo nos incluye
                if x.id != pipes[rr_pipe].ins.id:
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
                pipes[rr_pipe + 1].blocked = True
                break

        # Move to executed
        last_pipe = pipes[-1]
        if last_pipe.ins != EMPTY:
            # If last instructionn has been executed, exit
            if ins[-1] == last_pipe.ins:
                return

            executed.append(last_pipe.ins)
            pipes[-1].ins = EMPTY

        # Movemos las instrucciones que no esten bloqueadas
        for i in reversed(range(len(pipes))):
            curr_pipe = i
            prev_pipe = curr_pipe - 1

            if prev_pipe <= -1:
                break

            if not pipes[curr_pipe].blocked and pipes[curr_pipe].ins == EMPTY:
                pipes[curr_pipe].ins = pipes[prev_pipe].ins
                pipes[prev_pipe].ins = EMPTY

        # Load the new instruction
        li_pipe = get_li(pipes)
        if not pipes[li_pipe].blocked and pipes[li_pipe].ins == EMPTY:
            try:
                pipes[li_pipe].ins = ins[curr_ins]
                curr_ins += 1
            except:
                pipes[li_pipe].ins = EMPTY

        print_pipes(pipes, clock)

        clock += 1

        if clock >= 50:
            return


def main():
    instructions = parse_ins("data.asm")
    print(instructions)

    # Calculamos los peligros
    raw, war, waw = find_hazards(instructions)
    print("\n\n{:=<40}\n".format("RIESGOS"))
    print_riesgos("RAW", raw)
    print_riesgos("WAR", war)
    print_riesgos("WAW", waw)

    # Ejecutamos el codigo
    print("\n\n{:=<40}\n".format("EJECUCION"))
    pipes = [
        Pipeline("f1", False, EMPTY, PipeFunc.LI),
        Pipeline("f2", False, EMPTY, PipeFunc.ZZ),
        Pipeline("d1", False, EMPTY, PipeFunc.ZZ),
        Pipeline("d2", False, EMPTY, PipeFunc.RR),
        Pipeline("ex", False, EMPTY, PipeFunc.ZZ),
        Pipeline("mem1", False, EMPTY, PipeFunc.ZZ),
        Pipeline("mem2", False, EMPTY, PipeFunc.ZZ),
        Pipeline("wr", False, EMPTY, PipeFunc.WR)
    ]
    execute_table(instructions, raw, pipes)


if __name__ == "__main__":
    main()
