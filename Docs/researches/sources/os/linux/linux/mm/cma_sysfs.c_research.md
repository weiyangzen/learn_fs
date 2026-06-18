# File Research: sources/os/linux/linux/mm/cma_sysfs.c

## Purpose
Exposes per-CMA-area allocation/release counters and capacity information under the MM sysfs hierarchy.

## Main Interfaces
- Accounting hooks: `cma_sysfs_account_success_pages()`, `cma_sysfs_account_fail_pages()`, `cma_sysfs_account_release_pages()`.
- Read-only attributes: `alloc_pages_success`, `alloc_pages_fail`, `release_pages_success`, `total_pages`, `available_pages`.
- Init: `cma_sysfs_init()` creates the `cma` kobject under `mm_kobj` and one child kobject per activated CMA area.

## Control Flow
CMA core updates atomic64 counters on allocation success, allocation failure, and release. Sysfs show methods retrieve the owning `struct cma` from the enclosing `cma_kobject` and emit counter or capacity values. Initialization skips inactive CMA areas and unwinds already-created kobjects on failure.

## State And Synchronization
Counters are atomic64 values in `struct cma`. The kobject release method frees the dynamic `cma_kobject` and clears `cma->cma_kobj`.

## Integration Points
Hooks into CMA core accounting, `mm_kobj`, kobject sysfs operations, and activated CMA area enumeration.

## Risks And Review Focus
- `available_pages` reads `cma->available_count` without taking `cma->lock`, so it is informational rather than a synchronized allocation guarantee.
- Init failure unwinding must match kobject ownership and release semantics.
