# File Research: sources/os/bsd/openbsd-src/sys/sys/mutex.h

Defines OpenBSD spinning CPU-owned mutex interface and machine-independent implementation hooks.

Key contents:
- Documents mutex semantics: CPU-owned, non-recursive, spinning, CPU mutual exclusion only, optional interrupt blocking.
- `__MUTEX_IPL()` raises IPL to `IPL_MPFLOOR` on multiprocessor systems when needed.
- Under `__USE_MI_MUTEX`, defines `struct mutex`, owner/desired IPL/old IPL, and optional WITNESS object.
- WITNESS naming and flags: `MTX_NOWITNESS`, `MTX_DUPOK`.
- Diagnostic assertions for locked/unlocked state.
- DDB-only `struct db_mutex`.

Key APIs:
- `_mtx_init`, `mtx_init_flags`, `mtx_enter`, `mtx_enter_try`, `mtx_leave`.
- DDB helpers `db_mtx_enter` and `db_mtx_leave`.

Risk notes:
- Mutex nesting must be stack-like; interleaved unlock order is explicitly invalid.
