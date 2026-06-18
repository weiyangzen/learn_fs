# File Research: sources/os/bsd/netbsd-src/sys/sys/exec_elf.h

Read completely: 1534 lines.

## Purpose
Defines NetBSD's ELF ABI types, headers, constants, notes, auxiliary vectors, size-selection macros, and kernel ELF exec/core-dump interfaces.

## Main Interfaces
- ELF integer/address typedefs for 32-bit and 64-bit classes.
- File headers: `Elf32_Ehdr`, `Elf64_Ehdr`; program headers; section headers; symbols; relocations; dynamic entries; notes; versioning records.
- Identification constants: `EI_*`, `ELFMAG*`, `ELFCLASS*`, `ELFDATA*`, `ELFOSABI_*`, `ET_*`, extensive `EM_*`.
- Program/section constants: `PT_*`, `PF_*`, `SHT_*`, `SHF_*`, section indexes.
- Symbol/relocation helpers: `ELF*_R_*`, `ELF_ST_*`, visibility and versioning macros.
- Dynamic tags and flags: `DT_*`, `DF_*`, `DF_1_*`.
- Auxiliary vectors: `Aux32Info`, `Aux64Info`, `AT_*`.
- Notes: GNU ABI/build-id/hwcap, SuSE, Go build id, FDO packaging metadata, NetBSD ABI/emulation/PaX/MACHINE_ARCH/MCMODEL/core notes.
- Type-selection macros: `ELFSIZE`, `Elf_Ehdr`, `Elf_Phdr`, `ElfW`, `ELFNAME`, `AuxInfo`.
- Kernel limits and interfaces: `ELF_MAXPHNUM`, `ELF_MAXSHNUM`, `ELF_MAXNOTESIZE`, `ELF_AUX_ENTRIES`, `struct elf_args`, `exec_elf32_makecmds`, `exec_elf64_makecmds`, `elf*_populate_auxv`, `elf*_copyargs`, `elf*_check_header`, `coredump_elf*`.

## Dependencies And Integration
Includes machine ELF definitions and can coexist with `sys/elfdefinitions.h`. It is central to exec image loading, dynamic linker setup, ABI tagging, PaX policy, machine-architecture notes, and ELF core dumps.

## Risks And Edge Cases
- Some definitions are skipped if `sys/elfdefinitions.h` was already included, but NetBSD overrides `EM_ALPHA`.
- `ELF_NIDENT` is defined as `EI_INDENT`, which appears to preserve a prior spelling but is suspicious if consumers expect `EI_NIDENT`.
- Kernel caps program headers, section headers, and note size to limit memory-allocation abuse.
- ABI note sizes/names must match external toolchain expectations.
- `ELFSIZE` controls many generic type aliases; wrong selection changes structure interpretation.

## Filesystem Relevance
High. ELF is the primary executable/core format read from vnode files and affected by filesystem permissions, mount flags, and path/interpreter lookup.
