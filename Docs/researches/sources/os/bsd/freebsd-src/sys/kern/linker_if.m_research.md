# File Research: sources/os/bsd/freebsd-src/sys/kern/linker_if.m

## Purpose
Declares the FreeBSD kobj interface implemented by kernel linker classes. The `.m` file is an interface-definition source used to generate method dispatch glue for `struct linker_file` operations.

## Methods
- Symbol lookup: `lookup_symbol`, `lookup_debug_symbol`, `lookup_debug_symbol_ctf`.
- Symbol values and reverse lookup: `symbol_values`, `debug_symbol_values`, `search_symbol`.
- Function enumeration: `each_function_name`, `each_function_nameval`.
- Linker set lookup: `lookup_set`.
- Lifecycle: `unload`, static `load_file`, static `link_preload`, and `link_preload_finish`.
- CTF support: `ctf_get`, `ctf_lookup_typename`.
- Debug table export: `symtab_get`, `strtab_get`.
- VNET propagation hook: `propagate_vnets` when `VIMAGE` is enabled.

## Contract
Implementations return `ENOENT` for missing symbols/CTF data and zero on success. `load_file` should return zero without modifying the result when a class does not recognize the file type, and should set the result only after a recognized file is loaded.

## Implementations in This Group
`link_elf.c` implements this interface for ELF executable/shared-object style modules. `link_elf_obj.c` implements the same interface for ELF relocatable object modules. Both use these methods to integrate with the generic `kern_linker.c` subsystem.

## Filesystem / VM Relevance
The interface abstracts module loading from module storage. Filesystem-backed loaders implement `load_file`; preloaded-boot loaders implement `link_preload` and `link_preload_finish`; both expose loaded code/data for kernel debugging and VM/module lifecycle management.
