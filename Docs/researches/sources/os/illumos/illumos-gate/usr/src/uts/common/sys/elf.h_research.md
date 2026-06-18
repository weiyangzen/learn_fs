# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/elf.h

This header defines the generic ELF object-file ABI used by illumos for executables, shared objects, relocatable objects, core files, notes, capabilities, and architecture extension inclusion.

Key contents:
- File-size constants for ELF32 and ELF64 scalar types.
- ELF header layouts `Elf32_Ehdr` and conditionally `Elf64_Ehdr`.
- ELF identification indexes, magic constants, class/data/version/OSABI/ABI-version constants, file types, machine IDs, and object version constants.
- Extensive `EM_*` machine registry through current values such as RISC-V, BPF, LoongArch, and newer assigned machine IDs.
- Program header layouts `Elf32_Phdr` and `Elf64_Phdr`.
- Program header types including standard `PT_*`, Sun extensions, GNU compatibility values, stack/capability/DTrace segments, and processor ranges.
- Program header flags, including Solaris core-dump failure/killed/siginfo flags and extended program header index.
- Section header layouts `Elf32_Shdr` and `Elf64_Shdr`.
- Section types, Solaris ABI-specific section types, GNU overlapping OSABI-specific types, LLVM section extensions, processor/user ranges, section flags, and reserved section indexes.
- Symbol table layouts `Elf32_Sym` and `Elf64_Sym`, symbol info macros, binding/type/visibility constants.
- Relocation layouts `Elf32_Rel`, `Elf32_Rela`, `Elf64_Rel`, and `Elf64_Rela`, plus relocation info macros and SPARC V9 type-data helpers.
- Section group flag `GRP_COMDAT`.
- Note headers `Elf32_Nhdr` and `Elf64_Nhdr`.
- Move entries and move info macros.
- Capability entries, capability info/chain typedefs, capability info macros, capability section versions, capability group constants, Sun capability tags, and software capability bits.
- Core-note type constants for proc status, fpreg, psinfo, auxv, SPARC windows, LDT, pstatus, credentials, utsname, LWP data, privileges, core content, zone name, fd info, security flags, LWP name, user panic, and cwd.
- Kernel `elfheadcheck()` prototype.
- Conditional inclusion of `elf_SPARC.h`, `elf_386.h`, and `elf_amd64.h`.

Dependencies:
- Includes `sys/elftypes.h`.
- Uses C++ guards.
- 64-bit definitions require `_LP64` or `_LONGLONG_TYPE`.

Research notes:
- This is a core ABI header for the runtime linker, kernel exec/core handling, link-editor tooling, debuggers, and object-file consumers.
- Some Solaris and GNU section/program values overlap, and comments explicitly require OSABI knowledge for correct interpretation.
- The DTrace relationship appears through `SHT_SUNW_dof` and `PT_SUNWDTRACE`.
- Filesystem relevance is indirect but foundational: filesystems store ELF binaries and core files, while the kernel uses these structures during exec and core dump generation.
