# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/kobj.h

## Purpose
Defines the public/private kernel runtime linker object model, module metadata, kobj file-buffer helpers, symbol lookup APIs, and kobj memory/text allocation hooks.

## Main Interfaces
- `struct module_list`: linked list of module dependencies.
- `hotinline_desc_t`: hot-inline call descriptor.
- `symid_t`, `reloc_dest_t`, `module_mach`: symbol and relocation-related typedefs.
- `struct module`: loaded module record with ELF headers, sections, symbols, text/data/bss, dependencies, CTF, SDT, FBT, signature, and machine-specific data.
- `struct kobj_mem`: memory allocation tracking node.
- `struct _buf`: kobj file buffer state.
- `kobj_stat_t`: allocation/free counters.
- File buffer macros:
  - `kobj_getc()`
  - `kobj_ungetc()`
  - `B_OFFSET()`
  - `F_PAGE()`
  - `F_BLKS()`
- Kernel APIs:
  - module load/unload and lookup functions
  - symbol lookup and symbol name resolution
  - kobj file open/read/close/stat helpers
  - kobj allocation/free helpers
  - CTF and hot-inline setup
  - kobj virtual memory/text allocation
  - text window allocation/free
  - `kobj_printf()`

## Dependencies And Relationships
Includes module control, ELF, machine ELF, vmem, SDT, bootstat, and types headers. `struct module` is the central loaded-module representation used by krtld, module loading, symbol export, tracing metadata, and debugger/symbol consumers.

## Research Notes
The header is shared by early boot/runtime linker code and kernel module support. Architecture support is explicitly limited to i386, sparc, and amd64 for `kobj_vmem_init()`.
