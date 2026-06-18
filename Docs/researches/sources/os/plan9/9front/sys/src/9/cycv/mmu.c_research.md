# File Research: sources/os/plan9/9front/sys/src/9/cycv/mmu.c

Role: ARM Cyclone V MMU support for per-process L1/L2 page tables, TLB switching, kernel temporary mappings, `kmap`, direct physical/virtual address translation, and uncached allocation.

Key responsibilities:
- Initializes the CPU's current L1 table from `ttbget()` and installs a per-CPU temporary mapping L2 page at `TMAP`.
- Allocates, caches, switches, and frees per-process `L1` structures, with ASID rollover causing full TLB flush.
- Allocates L2 page-table pages lazily in `putmmu()`, installs user mappings, flushes old mappings, and handles text-cache coherency.
- Implements `flushmmu()` and `mmurelease()` cleanup for process address spaces, including per-process `KMAP` tables.
- Provides `paddr()`, `kaddr()`, and `cankaddr()` for direct-mapped kernel/peripheral address handling.
- Implements per-process `kmap()`/`kunmap()` and per-CPU `tmpmap()`/`tmpunmap()` for physical pages not directly addressable.
- Provides `ucalloc()` from a descending uncached/OCRAM region.

Dependencies:
- Relies on ARMv7-ish page-table constants/macros from `mem.h` and low-level TLB/cache functions from assembly.
- Uses Plan 9 `Proc`, `Page`, `Mach`, `Ref`, `newpage`, `freepages`, `smalloc`, and interrupt priority primitives.

Notes and risks:
- Many paths panic on misuse, including low interrupt level use in `l1free()`/`tmpmap()`, invalid direct address conversion, and exhausted kmap/tmpmap space.
- `l2free()` unlinks all used L2 pages into `mmufree` and clears four L1 entries per recorded `daddr`, matching 4-entry section coverage.
- `tmpmap()` also mirrors the kernel TMAP L1 entry into the current process L1 when needed.
