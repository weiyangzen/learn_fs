# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/elftypes.h

This header defines the base fixed-width-ish ELF scalar typedefs used by `sys/elf.h`.

Key contents:
- `Elf32_*` typedefs:
  - `Elf32_Addr`
  - `Elf32_Half`
  - `Elf32_Off`
  - `Elf32_Sword`
  - `Elf32_Word`
- `Elf64_*` typedefs under `_LP64` or `_LONGLONG_TYPE`:
  - `Elf64_Addr`
  - `Elf64_Half`
  - `Elf64_Off`
  - `Elf64_Sword`
  - `Elf64_Sxword`
  - `Elf64_Word`
  - `Elf64_Xword`
  - `Elf64_Lword`
  - `Elf32_Lword`

Dependencies:
- Includes `sys/feature_tests.h`.
- Uses C++ guards.

Research notes:
- Typedef choices vary by compilation model so that ELF32 types have the expected ABI size on both LP64 and non-LP64 builds.
- This is foundational ABI plumbing for all ELF structure definitions.
