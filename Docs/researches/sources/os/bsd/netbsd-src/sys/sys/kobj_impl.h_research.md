# File Research: sources/os/bsd/netbsd-src/sys/sys/kobj_impl.h

Private implementation header for kernel object loading. It defines program/relocation entry descriptors, object source type, read/close callbacks, and the full `struct kobj` containing ELF headers, segment addresses/sizes, symbol/string/section tables, relocation tables, load state, and source callbacks.

This is shared only with kernel grovellers and implementation code. Risks are internal layout coupling, architecture-specific ELF assumptions via `ARCH_ELFSIZE`, and correct cleanup of partially loaded VFS or memory-backed objects.
