# File Research: sources/os/bsd/openbsd-src/sys/sys/exec_elf.h

This header defines OpenBSD’s ELF ABI structures, constants, relocation helpers, dynamic tags, core notes, and kernel ELF exec hooks.

Key definitions:
- ELF integer typedefs for 32-bit and 64-bit classes.
- Identification constants: `EI_*`, `ELFMAG*`, `ELFCLASS*`, `ELFDATA*`, `ELFOSABI_*`, `IS_ELF`.
- ELF headers: `Elf32_Ehdr`, `Elf64_Ehdr`.
- Section headers, special section indexes, section types, section names, and section flags.
- Symbol table entries and symbol binding/type/visibility helpers.
- Relocation entries: `Elf32_Rel/Rela`, `Elf64_Rel/Rela`, `Elf32_Relr`, `Elf64_Relr`, and `ELF*_R_*` macros, including little-endian MIPS64 overrides.
- Program headers and segment constants including OpenBSD-specific `PT_OPENBSD_MUTABLE`, `RANDOMIZE`, `WXNEEDED`, `NOBTCFI`, `SYSCALLS`, and `BOOTDATA`.
- Dynamic section structures and `DT_*`, `DF_*`, `DF_1_*`.
- ELF note structures and OpenBSD core-note identifiers.
- `struct elfcore_procinfo`.
- Aux vector structures, `enum AuxID`, and `struct elf_args` under `_KERNEL` or `_DYN_LOADER`.
- ELFSIZE alias machinery mapping `Elf_*` names to 32- or 64-bit types.

Kernel APIs:
- `exec_elf_makecmds`
- `exec_elf_fixup`
- `coredump_elf`
- `coredump_note_elf_md`
- `coredump_writenote_elf`

Risk notes:
- This is a large ABI header used by kernel, dynamic loader, tools, and userland.
- OpenBSD program headers encode security policy: W^X exceptions, no branch-target CFI, syscall pin tables, randomization, and mutable segments.
- `ELF_AUX_ENTRIES` must match the actual aux vector construction path.
