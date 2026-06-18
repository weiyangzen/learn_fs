# File Research: sources/local-fs/squashfs-tools/squashfs-tools/memory_compat.h

Defines inline `get_physical_memory()` returning RAM size in MB. Linux first tries `sysconf(_SC_PHYS_PAGES)` and `_SC_PAGESIZE`, then falls back to `sysinfo()` because `sysconf(_SC_PHYS_PAGES)` may depend on `/proc`.

Non-Linux uses `sysconf()` only. Both paths use `long long` intermediate arithmetic for 32-bit PAE systems with more than 4 GB RAM.

Failure returns `0`, which `memory.c` treats as fatal for memory limit validation.
