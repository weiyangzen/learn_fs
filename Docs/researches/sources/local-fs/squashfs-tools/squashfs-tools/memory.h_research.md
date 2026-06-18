# File Research: sources/local-fs/squashfs-tools/squashfs-tools/memory.h

Small public header for the memory guard. It declares `check_usable_phys_mem(int total_mem, char *name)` and defines local `TRUE`/`FALSE` constants.

This file is intentionally minimal; policy is implemented in `memory.c`, platform probing in `memory_compat.h`.
