# File Research: sources/os/plan9/9front/sys/src/9/mt7688/mem.h

This header defines MT7688/MIPS memory layout, CPU register constants, page-table bits, TLB parameters, kernel/user address ranges, cache sizes, and trap cause values.

Key platform constants include `PHYSCONS`, `CONFADDR`, fixed `MEMSIZE` of 128 MB, 4K default pages with optional 16K pages, `KSTACK`, `MACHSIZE`, cache line and cache sizes, MIPS CP0 register numbers, status/cause bits, exception codes, direct-map segments, `MACHADDR`, `KMAPADDR`, and `SPBADDR`.

MMU definitions include MIPS page-mask encodings, `KUSEG/KSEG0/KSEG1/KSEG2/KSEG3`, PTE valid/write/cache/global bits, write-through default caching due to MIPS 24K erratum, ASID/TLB PID macros, hardware TLB size, soft TLB size, kmap size, and user stack/text/kernel text addresses.

Filesystem relevance is foundational: page size, cache policy, user stack limits, kmap layout, and copy-on-write PTE bits affect every filesystem server, page-cache path, and kernel/user copy operation.

Notable risks: the memory map is board-specific; write-back caching is disabled by default for erratum reasons; page size changes have comments warning 16K pages work poorly.
