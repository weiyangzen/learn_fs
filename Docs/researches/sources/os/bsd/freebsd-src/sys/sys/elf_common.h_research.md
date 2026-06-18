# File Research: sources/os/bsd/freebsd-src/sys/sys/elf_common.h

## Purpose
Defines ELF constants, note formats, dynamic tags, symbol/version metadata, auxiliary vector values, and relocation numbers that are independent of ELF word size. This is the shared namespace consumed by `elf32.h`, `elf64.h`, loaders, linkers, kernel image activation, core dump handling, and binary inspection tools.

## Main Interfaces
- `Elf_Note` / `Elf_Nhdr`: generic ELF note header.
- `Elf_GNU_Hash_Header`: GNU hash section header.
- ELF identity macros: `EI_*`, `ELFMAG*`, `IS_ELF`, `ELFCLASS*`, `ELFDATA*`, `ELFOSABI_*`.
- ELF object, machine, and architecture flag values: `ET_*`, `EM_*`, `EF_*`.
- Section constants: `SHN_*`, `SHT_*`, `SHF_*`, `GRP_COMDAT`, compression types.
- Program header and dynamic linker constants: `PT_*`, `PF_*`, `DT_*`, `DF_*`, `DF_1_*`.
- Note constants for FreeBSD, GNU, NetBSD, Solaris, FDO packaging metadata, and architecture properties.
- Symbol, visibility, syminfo, and versioning constants: `STB_*`, `STT_*`, `STV_*`, `VER_*`, `SYMINFO_*`.
- Auxv entries: `AT_*`, `AT_COUNT`.
- Relocation values for i386, amd64/x86-64, AArch64, ARM, IA-64, LoongArch, MIPS, PowerPC, RISC-V, and SPARC.
- BSD ELF flags: `ELF_BSDF_SIGFASTBLK`, `ELF_BSDF_VMNOOVERCOMMIT`.

## Dependencies And Integration
The file assumes fixed-width FreeBSD integer typedefs such as `u_int32_t` are already available from including context. It intentionally avoids architecture-specific structure layout, leaving width-specific typedefs to other ELF headers. It is included by many kernel and userland ELF consumers, so numeric values are ABI and toolchain contract.

## Implementation Notes
There is almost no executable logic beyond `IS_ELF`. The file is a compatibility table. The highest-risk edits are numeric changes, reuse of reserved values, or accidental divergence from ELF psABI/GABI assignments. FreeBSD-specific note and section values also participate in kernel/userland ABI, especially core dump notes and exec feature controls.
