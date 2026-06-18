# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/ufs/lufs_map.c

## Purpose

`lufs_map.c` implements the UFS logging map layer: generic map allocation, the deltamap of dirty metadata not yet logged, the logmap of deltas already in the log, cancellation records, cached roll buffers, log commit records, roll-thread coordination, and log scan reconstruction.

## Main Interfaces

Core routines include `map_get`, `map_put`, `map_free_entries`, `deltamap_add`, `deltamap_remove`, `deltamap_del`, `deltamap_push`, `logmap_add`, `logmap_add_buf`, `logmap_commit`, `logmap_cancel`, `logmap_iscancel`, `logmap_list_get`, `logmap_list_get_roll`, `logmap_setup_read`, `logmap_remove_roll`, `logmap_sethead`, `logmap_settail`, `logmap_roll_dev`, `logmap_logscan`, `_init_map`, and `handle_dquot`.

## Behavior And Data Flow

`deltamap_add()` splits metadata ranges at `MAPBLOCKSIZE` boundaries and records dirty deltas with optional push functions. At sync end, `deltamap_push()` invokes those functions to move all remaining deltas into the logmap.

`logmap_add()` and `logmap_add_buf()` write deltas into the log through `ldl_write()`, insert them into logmap hash/list structures, cancel older overlapping entries, and track transaction id/age. `logmap_add_buf()` optionally attaches a memory-capped cached roll buffer so the roll thread can write master data without rereading and overlaying deltas.

`logmap_commit()` writes a commit delta, rounds/pushes the log buffer, and resets dirty counters after successful commit. `logmap_logscan()` rebuilds the logmap from on-disk deltas and discards the last partial transaction.

## Roll And Cancel Semantics

The roll thread asks `logmap_next_roll()` for stable, committed deltas, uses `logmap_list_get_roll()` to age/mark entries, then `logmap_remove_roll()` frees rolled entries. `logmap_setup_read()` decides whether rolling needs a master read and builds a sector map to avoid overwriting user data between metadata sectors.

Cancel records prevent reuse or stale replay of blocks whose metadata was superseded. User-data cancel placeholders protect deleted user blocks within a transaction without logging user data. `logmap_free_cancel()` frees canceled entries only after the commit record is known durable.

## Notable Invariants And Risks

- `mtm_mutex` protects hash/list fields; `mtm_rwlock` blocks readers while aged entries are being rolled or freed.
- Entries for current transaction or commit-in-progress are not rolled.
- Cached roll buffers are reference-counted and invalidated on cancellation.
- Quota deltas carrying dquot references require `handle_dquot()` cleanup when replaced by non-quota deltas.
- Audit hotspots are overlap/cancel rules, `ME_AGE` lock upgrade paths, CRB memory accounting, partial transaction abort, and dquot reference cleanup.
