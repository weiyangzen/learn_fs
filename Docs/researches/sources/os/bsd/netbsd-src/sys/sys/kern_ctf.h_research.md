# File Research: sources/os/bsd/netbsd-src/sys/sys/kern_ctf.h

Defines kernel Compact C Type Format metadata plumbing for modules. `mod_ctf_t` records decompressed CTF data, symbol/string tables, symbol name maps, CTF/type offsets, allocation ownership, FBT provider status, and enabled count. `mod_ctf_get` retrieves CTF metadata for a module.

It integrates module loading, ksyms, DTrace/FBT-style tracing, and type introspection. Risks are lifetime ownership of decompressed tables and keeping symbol/string table counts synchronized with module object state.
