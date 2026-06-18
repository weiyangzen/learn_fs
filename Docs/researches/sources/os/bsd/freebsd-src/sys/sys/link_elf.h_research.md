# File Research: sources/os/bsd/freebsd-src/sys/sys/link_elf.h

Defines ELF runtime linker/debugger public structures and helper prototypes. It includes `sys/elf.h`, search-origin flags for `Dl_serinfo`, and the `Link_map` structure representing loaded shared objects.

`struct r_debug` is the debugger rendezvous state with loaded-image map, breakpoint callback, add/delete/consistent state, and rtld base. `struct dl_phdr_info` is the callback payload for iterating program headers and includes relocation base, module name, phdr pointer/count, load/unload counters, and TLS metadata.

Exports `dl_iterate_phdr`, `_rtld_addr_phdr`, `_rtld_get_stack_prot`, `_rtld_is_dlopened`, and rtld variable get/set helpers, with ARM EABI unwind index lookup where applicable.
