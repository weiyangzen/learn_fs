# File Research: sources/local-fs/squashfs-tools/squashfs-tools/memory.c

Implements `check_usable_phys_mem(int total_mem, char *name)`, a guard for mksquashfs cache memory settings. It obtains physical memory via `get_physical_memory()`, rejects failure, then caps requested memory at 75% of physical RAM.

It also adds a 32-bit process guard: if `sizeof(void *) == 4`, requests above 2048 MB are rejected even when physical RAM is larger, because addressable user space may be only 2-3 GB.

Dependencies: `error.h` for `ERROR`, `memory_compat.h` for platform memory detection, and `memory.h` for declaration/boolean constants. Behavior is fail-fast but returns `FALSE` rather than exiting directly.
