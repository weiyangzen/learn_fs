# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/elf_amd64.h

This header defines AMD64/x86-64-specific ELF relocation constants, aliases, maximum page size, section/index flags, and 64-bit PLT/GOT layout details.

Key contents:
- Includes `sys/elf_386.h` for shared x86 definitions.
- `R_AMD64_*` relocation constants including absolute, PC-relative, GOT/PLT, copy/global/jump slot/relative, TLS, size, descriptor TLS, `IRELATIVE`, `RELATIVE64`, GOTPCRELX, and REX_GOTPCRELX.
- Compatibility aliases mapping `R_X86_64_*` names to `R_AMD64_*`.
- `ELF_AMD64_MAXPGSZ`.
- Processor-specific section type `SHT_AMD64_UNWIND` and alias `SHT_X86_64_UNWIND`.
- Large-section flags and common aliases:
  - `SHF_AMD64_LARGE`
  - `SHF_X86_64_LARGE`
- Large common section indexes:
  - `SHN_AMD64_LCOMMON`
  - `SHN_X86_64_LCOMMON`
- 64-bit PLT/GOT constants when `elf_386.h` established the x86 common block.
- Common `M_*` aliases for `_ELF64`.

Dependencies:
- Includes `sys/elf_386.h`.
- Uses C++ guards.

Research notes:
- Maintains both Solaris `R_AMD64_*` and System V AMD64 psABI `R_X86_64_*` names for compatibility.
- `PT_SUNW_UNWIND` is intentionally defined in the generic OS-specific range in `elf.h`.
- ABI-sensitive for link-editor/runtime-linker relocation behavior.
