# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/elf_SPARC.h

This header defines SPARC-specific ELF flags, relocations, section/symbol/dynamic values, register symbol numbers, and PLT/GOT layout constants for 32-bit and 64-bit SPARC.

Key contents:
- SPARC `e_flags` masks and values for V8+ and vendor extensions.
- SPARC V9 memory model flags for TSO, PSO, and RMO.
- `R_SPARC_*` relocation constants from basic relocations through 64-bit, TLS, GOT-data, size, and `H34`; plus `R_SPARC_NUM`.
- Alias `R_SPARC_L34`.
- SPARC and SPARCV9 maximum page sizes.
- Processor-specific section type `SHT_SPARC_GOTDATA`.
- Section flags/indexes `SHF_ORDERED`, `SHF_EXCLUDE`, `SHN_BEFORE`, and `SHN_AFTER`.
- SPARC register symbol type and dynamic tag:
  - `STT_SPARC_REGISTER`
  - `DT_SPARC_REGISTER`
- Register symbol numbers for `%g1` through `%g7`.
- Architecture-common PLT/GOT constants:
  - PLT instruction size and reserved counts.
  - GOT dynamic entry index.
  - 32-bit PLT/GOT alignment and entry sizes.
  - 64-bit PLT/GOT alignment, entry sizes, near/far PLT sizing, and far PLT block constants.
- Common aliases selected by `_ELF64`.

Dependencies:
- No includes of its own.
- Uses C++ guards.

Research notes:
- Like the x86 ELF headers, this is consumed by linkers, runtime linkers, loaders, and debuggers.
- The `_SYS_ELF_MACH_COMMON` guard prevents conflicting generic `M_*` definitions when multiple architecture headers are included.
