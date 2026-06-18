# File Research: sources/os/bsd/dragonflybsd/sys/sys/imgact_elf.h

`imgact_elf.h` defines kernel ELF image activation and coredump support structures. It includes `elf_common.h` and `machine/elf.h`.

Under `_KERNEL`, it defines `AUXARGS_ENTRY()`, ELF auxiliary argument and brand-info structures, brand note metadata, generic typedefs through `__ElfType()`, maximum brand count, brand flags, and brand-note flags.

It declares brand registration/removal/in-use functions, DragonFly stack fixup, ELF coredump routines, generic coredump support, and the DragonFly brand note. This header connects ELF format parsing with exec emulation/branding and core generation.
