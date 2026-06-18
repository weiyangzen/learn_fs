# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/machelf.h

Purpose: Provides machine-class-transparent ELF typedefs and macros so common code can use native `Ehdr`, `Shdr`, `Sym`, `Phdr`, `Dyn`, etc. independent of ELF32/ELF64 build mode.

Key behavior:
- Selects architecture ELF header definitions for amd64/i386/sparc.
- Under `_ELF64` without `_ELF32_COMPAT`, maps generic names to `Elf64_*`; otherwise maps to `Elf32_*`.
- In kernel builds, maps relocation and symbol helper macros to `ELF32_*` or `ELF64_*`.
- Defines `EC_*` printf cast macros for shared format strings across ELF classes.

Important detail: `EC_NATPTR()` casts via `uintptr_t` for native pointers to avoid compiler complaints about direct pointer-to-wide-integer casts.

Relevance to subset A: Core executable/module support; indirectly relevant to kernel module loading and exec handling.
