# File Research: sources/os/plan9/plan9/sys/src/cmd/8l/asm.c

Purpose: final executable/data writer for the 386 linker.

Key behavior: provides endian output helpers, `entryvalue`, `asmb`, `cflush`, `datblk`, and `rnd`. `asmb` emits text instructions, data blocks, optional symbols/line tables/dynamic relocation data, then writes one of several headers: old Unix, COFF, Plan 9, DOS COM/EXE, or ELF. `datblk` materializes initialized data, constants, string data, and address relocations.

Integration notes: called after layout in `span.c` and data placement in `pass.c`. Dynamic-module mode routes address initializers through `dynreloc`. Header constants must agree with command-line `HEADTYPE`, `INITTEXT`, `INITDAT`, and `INITRND`.
