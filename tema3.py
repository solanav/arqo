from enum import Enum
from math import log2


class TipoPage(Enum):
    Fixed = 0  # Fixed-size pages
    Variable = 1  # Variable-size segments
    Segment = 2  # Segments with fixed-size pages


class PageTable:
    def __init__(self):
        self.tipo = TipoPage.Fixed

        # Sizes
        self.vm_size = -1
        self.real_size = -1
        self.page_size = -1

        # Addr
        self.vm_addr_size = -1
        self.real_addr_size = -1
        self.addr_offset = -1

    def update(self):
        if self.vm_size != -1 and self.real_size != -1 and self.page_size != -1:
            self.update_addr()

    def update_addr(self):
        self.vm_addr_size = log2(self.vm_size)
        self.real_addr_size = log2(self.real_size)
        self.addr_offset = log2(self.page_size)

    def __str__(self):
        return """
TYPE                {}
REAL MEMORY SIZE    {}KB
VIRTUAL MEMORY SIZE {}KB
[VTotal - {}] - [Page - {} | Offset - {}]
[RTotal - {}] - [Page - {} | Offset - {}]
        """.format(
            self.tipo,
            self.real_size / 1024,
            self.vm_size / 1024,
            self.vm_addr_size,
            self.vm_addr_size - self.addr_offset,
            self.addr_offset,
            self.real_addr_size,
            self.real_addr_size - self.addr_offset,
            self.addr_offset
        )


class TipoCache(Enum):
    FullyAssociative = 0  # Tag y offset
    SetAssociative = 1  # Tag, index y offset
    DirectMapped = 2  # Tag, index y offset


class Cache:
    def __init__(self):
        # Type of cache
        self.tipo = TipoCache.FullyAssociative

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
        self.nway = 1

    def update(self):
        if self.main_size != -1 and self.block_size != -1 and self.cache_size != -1:
            self.update_addr()

    def update_addr(self):
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
TYPE              {}
MAIN MEMORY SIZE  {}KB
CACHE MEMORY SIZE {}KB
CACHE BLOCK SIZE  {}
CACHE BLOCKS      {}
[Total - {}] - [Tag - {} | Index - {} | Offset - {}]
        """.format(
            self.tipo,
            self.main_size / 1024,
            self.cache_size / 1024,
            self.block_size,
            (self.cache_size / self.block_size) * self.nway,
            self.addr_size,
            self.tag_size,
            self.index_size,
            self.offset_size
        )


def main():
    # Call the test to check everything is a-ok
    test()

    # Exercises about cache without tlb or shit like that
    c = Cache()

    c.tipo = TipoCache.SetAssociative
    c.main_size = 2 ** 24  # Tamanno total de la memoria
    c.cache_size = 2 * 16 * 16  # Tamanno total de la cache
    c.block_size = 16  # Tamanno de un bloque individual de la cache
    c.nway = 2  # Numero de vias

    c.update()
    print(c)

    # TLB and virutual pages bullshit
    p = PageTable()
    p.vm_size = 2 ** 32
    p.real_size = 2 ** 24
    p.page_size = 2 ** 12

    p.update()
    print(p)


def test():
    # Ejercicio 3.1.5
    c = Cache()
    c.main_size = 16 * 1024 * 1024
    c.cache_size = 8 * 1024

    c.tipo = TipoCache.DirectMapped
    c.block_size = 1 * 4
    c.update()
    assert c.addr_size == 24.0
    assert c.tag_size == 11.0
    assert c.index_size == 11.0
    assert c.offset_size == 2.0

    c.tipo = TipoCache.DirectMapped
    c.block_size = 8 * 4
    c.update()
    assert c.addr_size == 24.0
    assert c.tag_size == 11.0
    assert c.index_size == 8.0
    assert c.offset_size == 5.0

    c.tipo = TipoCache.SetAssociative
    c.block_size = 2 * 4
    c.nway = 4
    c.update()
    assert c.addr_size == 24.0
    assert c.tag_size == 13.0
    assert c.index_size == 8.0
    assert c.offset_size == 3.0

    c.tipo = TipoCache.FullyAssociative
    c.block_size = 4 * 4
    c.update()
    assert c.addr_size == 24.0
    assert c.tag_size == 20.0
    assert c.index_size == 0
    assert c.offset_size == 4.0


if __name__ == "__main__":
    main()
