# File Research: sources/os/bsd/dragonflybsd/sys/sys/mman.h

Defines memory mapping and memory advice user ABI. Includes `mode_t`, `off_t`, and `size_t` fallbacks; protection flags; mapping flags including DragonFly/BSD extensions such as `MAP_VPAGETABLE`, `MAP_TRYFIXED`, `MAP_NOCORE`, `MAP_SIZEALIGN`, and `MAP_32BIT`; mlock flags; msync flags; madvise/posix_madvise constants; mincore bits; and mmap-family function declarations.

Filesystem relevance is high because file-backed mappings, msync, mmap, mincore, and vnode-backed VM behavior are part of the VFS/VM boundary.
