# File Research: sources/os/bsd/freebsd-src/sys/sys/imgact_elf.h

Kernel-only ELF image activation support header. It wraps machine ELF types and defines aux-vector helper macros, including pointer handling for LP64 kernels executing 32-bit ELF.

Key structures are `ElfN(Auxargs)` for loader-to-stack fixup data, `Elf_Brandnote` for ABI note recognition/translation, and `ElfN(Brandinfo)` for executable brand matching, interpreter path selection, sysent vector binding, and brand flags.

Exports cover brand registration/removal, FreeBSD auxarg fixups, core dump writing, note population/parsing, segment sizing, note registration, per-thread dump hooks, fallback brand, and FreeBSD/kFreeBSD brand notes.
