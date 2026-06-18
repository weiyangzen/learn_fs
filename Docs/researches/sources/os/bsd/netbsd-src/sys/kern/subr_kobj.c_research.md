# File Research: sources/os/bsd/netbsd-src/sys/kern/subr_kobj.c

Read completely: 1280 lines.

Implements the modular-kernel ELF relocatable object loader. Under `MODULAR`, it loads ET_REL objects from memory or a provider-specific read function, maps sections, resolves symbols, applies relocations, registers kernel symbols, and unloads module memory.

Core behavior:
- `kobj_load_mem()` creates a memory-backed object; VFS-backed loading is implemented separately.
- `kobj_load()` validates ELF header/version/type/machine, reads section headers, symbol/string tables, section-name strings, and relocation tables.
- PROGBITS/NOBITS sections are mapped into separate text, data, and rodata VM regions, with symbols adjusted to their loaded addresses.
- Local relocations happen during `kobj_load()`; undefined globals are resolved and global relocations are applied later by `kobj_affix()`.
- `kobj_affix()` renames the object, checks for symbol conflicts, applies global relocations, registers ksyms, jettisons relocation/header data, calls machine-dependent finalization, and changes text/rodata protections.
- `kobj_unload()` closes sources, frees relocation/header/symbol/string data, unregisters ksyms, calls machine-dependent unload notifications, and frees mapped segments.

Risks and notes:
- Only one symbol table is supported; weak undefined symbols are rejected.
- Duplicate global definitions are rejected except for selected linker-generated boundary symbols.
- Error paths unload the whole object.
- Non-`MODULAR` builds provide stubs that return `ENOSYS` or panic for impossible module operations.
