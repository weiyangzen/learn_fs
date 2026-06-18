# File Research: sources/os/plan9/plan9/sys/src/9/pcboot/dat.h

## Purpose
Central bootstrap data definitions for the PC boot kernel: machine/process structures, configuration storage, memory-map structures, boot loader state, Multiboot layout, and shared globals.

## Main Interfaces
- Defines `BOOTLINE`, `BOOTARGS`, `BOOTARGSLEN`, `MAXCONF`, `confname`, `confval`, and `nconf`.
- Defines PC kernel-ish structures used by the boot environment: `Lock`, `Label`, `FPsave`, `Conf`, `Mach`, `PCArch`, `ISAConf`, `Mbi`, `Mod`, `MMap`, `Boot`.
- Defines boot state constants used by `bootld.c`.
- Declares major globals such as `arch`, `machp`, `m`, `mmap`, `nmmap`, `multibootheader`, `conschan`, `memstart`, and `memend`.

## Implementation Notes
- The file imports `../port/portdat.h` after defining PC-specific prerequisite types.
- `Boot` contains the current loader state, exec header scratch, entry, and active buffer pointers.
- Multiboot flags and structures match the handoff built before jumping to the loaded kernel.
- `BADPTR(x)` treats addresses below `0x80000000` as invalid kernel pointers in this bootstrap context.

## Dependencies And Risks
- This header is shared by many boot files and must remain ABI-consistent with assembly and `mem.h`.
- Some structures mirror full kernel layouts only as much as the bootstrap needs.
