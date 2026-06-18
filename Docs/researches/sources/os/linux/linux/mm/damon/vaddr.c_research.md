# File Research: sources/os/linux/linux/mm/damon/vaddr.c

Implements DAMON monitoring operations for process virtual address spaces (`DAMON_OPS_VADDR`) and fixed virtual address ranges (`DAMON_OPS_FVADDR`). It derives monitoring regions from VMAs, samples page-table young/idle state, validates target lifetime, and applies supported DAMOS actions through `madvise`, stat walks, and NUMA migration.

Key responsibilities:
- Converts a target `struct pid` into task and `mm_struct` references safely.
- Initializes and updates monitored regions for task address spaces using the three-region abstraction.
- Prepares access checks by selecting a random sampling address per region and clearing young/idle state at that address.
- Checks accesses by walking page tables and reading PTE/PMD/Hugetlb young state, folio idle state, and MMU notifier young state.
- Implements virtual-address DAMOS actions: `WILLNEED`, `COLD`, `PAGEOUT`, `HUGEPAGE`, `NOHUGEPAGE`, `MIGRATE_HOT`, `MIGRATE_COLD`, and `STAT`.
- Provides scheme scoring for pageout and migration actions.
- Registers both `vaddr` and `fvaddr` DAMON operation sets at subsystem init.

Region initialization:
- `__damon_va_three_regions()` walks VMAs under RCU, identifies the two largest unmapped gaps, sorts them by address, and returns three aligned ranges spanning mapped areas outside those gaps.
- `damon_va_three_regions()` obtains and locks the target mm, calls the helper, and drops the mm reference.
- `damon_va_init()` initializes target regions only if the user did not provide explicit regions.
- `damon_va_update()` periodically recalculates the three ranges and applies them with `damon_set_regions()`.
- `DAMON_OPS_FVADDR` disables automatic init/update so user-provided fixed virtual ranges are preserved.

Access sampling:
- `damon_va_mkold()` walks one address and clears young state for PTE, PMD THP, and HugeTLB entries where applicable.
- `__damon_va_prepare_access_check()` picks `r->sampling_addr` with `damon_rand()` and marks it old.
- `damon_va_young()` walks one address and reports whether it was accessed through PTE/PMD young bits, folio idle state, or MMU notifier state; it also returns folio size.
- `__damon_va_check_access()` caches the last checked folio-sized range for a target so adjacent regions sampling the same folio reuse the same result.
- Missing `mm_struct` is treated as not accessed for affected regions.

DAMOS application:
- `damos_madvise()` invokes `do_madvise()` for supported advice-based actions and returns the page-aligned applied byte length on success.
- `damos_va_filter_out()` evaluates ops filters against folios, with a vaddr-specific fast path for the young filter because the backend already has page-table access.
- `damos_va_stat()` walks page tables to count bytes that pass ops filters for `DAMOS_STAT`.
- `damos_va_migrate()` isolates folios into per-destination lists while walking the region and migrates them with `damon_migrate_pages()`.
- Weighted migration destinations use a weighted-interleave calculation based on VMA offset and folio order; if no destination list is configured, migration uses the scheme's `target_nid`.
- Duplicate folio accounting is avoided with `scheme->last_applied`.

Target lifecycle:
- `damon_va_target_valid()` checks whether the target PID still resolves to a task.
- `damon_va_cleanup_target()` drops the PID reference.
- `damon_va_apply_scheme()` dispatches action handling and returns zero for actions unsupported by vaddr.

Architecture and configuration notes:
- Transparent hugepage and HugeTLB paths are conditionally compiled.
- `CONFIG_ADVISE_SYSCALLS` controls whether advice-based DAMOS actions can call `do_madvise()`; otherwise the stub returns zero applied bytes.
- Page-table walking uses `PGWALK_RDLOCK` and mmap read locks.
- The file includes `tests/vaddr-kunit.h` for static-helper tests.
