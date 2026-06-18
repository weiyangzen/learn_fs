# File Research: sources/os/bsd/dragonflybsd/sys/sys/malloc.h

Defines DragonFly kernel malloc flags, malloc type declaration/definition macros, common malloc types, slab/contiguous allocation APIs, kmalloc object-zone helpers, debug and non-debug allocation wrappers, zeroing optimizations, realloc/string duplication helpers, free helpers, usable-size/limit APIs, and slab cleanup.

Filesystem relevance is broad: VFS, vnode, mount, journal, namecache, and filesystem implementations allocate typed kernel memory through this interface. Notable semantics: `M_NOWAIT` can fail often on DragonFly; `M_SYSALLOC`/reserve flags exist for critical kernel infrastructure; object allocations use separate `_obj` malloc types.
