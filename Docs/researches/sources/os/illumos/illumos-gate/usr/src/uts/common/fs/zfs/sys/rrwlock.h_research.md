# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/rrwlock.h

This header declares ZFS re-entrant reader/writer locks and reader-mostly locks built on top of them.

Core definitions:
- `rrwlock_t` contains a mutex, CV, current writer thread, anonymous-reader refcount, linked-reader refcount, writer-wanted flag, and `track_all` mode.
- `rrw_enter_read_prio()` is the priority read path for readers that may need to bypass waiting writers.
- Held macros wrap `rrw_held()` for read, write, and any-lock checks.
- `rrmlock_t` contains `RRM_NUM_LOCKS` (`17`) `rrwlock_t` shards for scalable read acquisition.

Public API surface:
- `rrw_init()`, `rrw_destroy()`, generic/read/write/prio-read enter, exit, held query, and TSD destructor.
- `rrm_init()`, `rrm_destroy()`, generic/read/write enter, exit, and held query.

Risk-sensitive invariants:
- Tags passed to `rrw_enter()` and `rrw_exit()` must match for tracked reader references.
- `rrwlock_t` allows re-entrant reads but not writer re-entrancy or upgrades.
- `rrmlock_t` pessimizes writers by acquiring all shards; read release must correspond to the thread/shard used at acquire time.
