# File Research: sources/os/bsd/dragonflybsd/sys/sys/link_elf.h

Defines ELF runtime linker/debugger public structures and helpers. Includes SunOS-compatible search path flags, `Link_map`, `r_debug`, `dl_phdr_info`, callback type for `dl_iterate_phdr`, and rtld helper declarations.

Mostly user/runtime-linker ABI. Indirectly relevant to kernel/module research through ELF format conventions, but kernel KLD details are in `linker.h`.
