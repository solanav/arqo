from enum import Enum
from math import log2


class TipoCache(Enum):
    FullyAssociative = 0  # Tag y offset
    SetAssociative = 1  # Tag, index y offset
    DirectMapped = 2  # Tag, index y offset


class Cache:
    def __init__(self, tipo: TipoCache):
        # Type of cache
        self.tipo = tipo

        # Sizes (in bytes)
        self.main_size = -1
        self.cache_size = -1
        self.block_size = -1

        # Address and shit (in bits)
        self.addr_size = -1
        self.tag_size = -1
        self.index_size = -1
        self.offset_size = -1

        # Other data
        self.comparators = -1
        self.nway = -1

    def update(self):
        self.comparators = log2(self.main_size / self.block_size)
        self.addr_size = log2(self.main_size)
        self.offset_size = log2(self.block_size)

        if self.tipo == TipoCache.DirectMapped:
            self.index_size = log2(self.cache_size / self.block_size)

        if self.tipo == TipoCache.SetAssociative:
            self.index_size = log2(self.cache_size / (self.block_size * self.nway))

        if self.tipo == TipoCache.FullyAssociative:
            self.index_size = 0

        self.tag_size = self.addr_size - (self.offset_size + self.index_size)

    def __str__(self):
        return """
TYPE: {}
MAIN MEMORY SIZE:  {}KB
CACHE MEMORY SIZE: {}KB
CACHE BLOCK SIZE:  {}
[{}] - [{} | {} | {}]
        """.format(
            self.tipo,
            self.main_size / 1024,
            self.cache_size / 1024,
            self.block_size,
            self.addr_size,
            self.tag_size,
            self.index_size,
            self.offset_size
        )


def main():
    c = Cache(TipoCache.FullyAssociative)
    c.main_size = 32 * 1024
    c.cache_size = 4 * 1024
    c.block_size = 16

    c.update()

    print(c)


if __name__ == "__main__":
    main()
