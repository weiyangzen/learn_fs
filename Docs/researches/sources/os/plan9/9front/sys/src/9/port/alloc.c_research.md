# File Research: sources/os/plan9/9front/sys/src/9/port/alloc.c

Kernel heap/pool allocation wrapper layer.

Key behavior:
- Defines three pools: `mainmem`, `imagmem`, and `secrmem`, each backed by `xalloc`/`xmerge` and protected by pool-specific interrupt locks.
- Pool print/panic callbacks buffer messages while locked and print or panic after releasing the lock.
- `mallocsummary` and `poolsummary` report pool capacity and allocation statistics.
- Implements kernel `smalloc`, `malloc`, `mallocz`, `mallocalign`, `free`, `realloc`, and `msize` on top of pool allocation.
- Maintains two-word allocation padding for malloc/realloc caller tags.
- Implements secret-memory allocation and free through `secrmem`.
- Provides tag setters/getters for allocation diagnostics.

Notable dependencies:
- Generic pool allocator from `<pool.h>`.
- Low-level physical allocation `xalloc` and merging `xmerge`.

Research notes:
- `smalloc` and `secalloc` wait until memory is available; `malloc`/`mallocz` return nil on failure.
- Secret memory uses a distinct pool with `POOL_ANTAGONISM`, but this file only zeroes on allocation, not explicitly on free.
