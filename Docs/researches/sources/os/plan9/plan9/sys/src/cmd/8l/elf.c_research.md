# File Research: sources/os/plan9/plan9/sys/src/cmd/8l/elf.c

Purpose: generic ELF32/ELF64 header, program-header, and optional section-header emission for Plan 9 linkers.

Key behavior: `elfident` writes ELF identity; `elf32` and `elf64` choose endian writers, emit executable headers, three default program headers for text/data/symbol payloads, optional caller-supplied program sections, and optional section tables under debug `S`.

Integration notes: `8l/asm.c` calls `elf32(I386, ELFDATA2LSB, ...)` for `HEADTYPE 5`. Physical data address is inferred from `INITTEXT`/`INITTEXTP`; section headers are mainly diagnostic/debug support.
