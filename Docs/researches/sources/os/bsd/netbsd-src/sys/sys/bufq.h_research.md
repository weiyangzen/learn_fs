# File Research: sources/os/bsd/netbsd-src/sys/sys/bufq.h

## Scope

Declares the kernel device-driver buffer queue interface.

## APIs And Behavior

- Kernel-only header; emits an error outside `_KERNEL`.
- Defines strategy constants `BUFQ_STRAT_ANY` and `BUFQ_DISK_DEFAULT_STRAT`.
- Defines allocation flags for raw-block sorting, cylinder sorting, exact strategy selection, and masks.
- Declares `bufq_init`, `bufq_alloc`, `bufq_drain`, `bufq_free`, `bufq_put`, `bufq_get`, `bufq_peek`, `bufq_cancel`, `bufq_getstrategyname`, and `bufq_move`.

## Dependencies

- Forward-declares `struct buf` and `struct bufq_state`.

## Risks And Invariants

- Sorting semantics depend on `struct buf` fields such as `b_rawblkno` and `b_cylinder`.
- `BUFQ_EXACT` prevents fallback to other strategies.
