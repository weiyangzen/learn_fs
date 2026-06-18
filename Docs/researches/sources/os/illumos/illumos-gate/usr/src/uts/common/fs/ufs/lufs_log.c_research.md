# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/ufs/lufs_log.c

## Purpose

`lufs_log.c` implements the low-level logical log device layer for UFS logging. It maps logical log offsets through extent tables, manages circular read/write buffers, writes delta records and sector trailers, scans logs at mount, advances head/tail state, and transitions the filesystem into log-error state on I/O failure.

## Main Interfaces

Important routines include `ldl_strategy`, `ldl_write`, `ldl_read`, `ldl_waito`, `ldl_round_commit`, `ldl_push_commit`, `ldl_has_space`, `ldl_need_commit`, `ldl_sethead`, `ldl_settail`, `ldl_savestate`, `ldl_logscan_begin`, `ldl_logscan_read`, `ldl_logscan_end`, `ldl_need_roll`, `ldl_seterror`, `ldl_bufsize`, `alloc_wrbuf`, `alloc_rdbuf`, and `free_cirbuf`.

## Behavior And Data Flow

`ldl_strategy()` clones a logical log I/O into one or more physical device I/Os according to the in-core log extent table. It also routes writes through the snapshot layer when snapshots are active and uses task-specific bypass state to avoid snapshot throttling deadlocks.

`ldl_write()` writes a delta header, then optional delta data, into the circular write buffer. `storebuf()` inserts sector trailers containing transaction id and monotonically increasing sector identity. Full or wrapped buffers are asynchronously pushed with `writelog()`.

`ldl_read()` reconstructs data from log offsets, handling cached roll buffers, zero deltas, sector trailers, and wraparound. `ldl_logscan_read()` validates sector identities during mount scan so partial or torn transactions are rejected.

## State Management

`ldl_sethead()` advances the durable log head after deltas are rolled to the master device, invalidates affected cached buffers, updates head identity/tid, and saves duplicated state sectors. `ldl_settail()` establishes the tail after log scan. `ldl_savestate()` writes the in-core `ml_odunit_t` state twice into the state buffer with checksum.

## Notable Invariants And Risks

- Writers are single-threaded through `un_log_mutex`.
- One extra sector is reserved so `head == tail` can mean empty, not full.
- Sector trailers are part of the logical stream and must be skipped by readers.
- `LDL_ERROR` causes future log I/O to fail, marks `un_badlog` on disk, saves state, warns the operator, and asks UFS to hard-lock itself outside scan.
- Audit hotspots are wraparound math, sector identity validation, cloned I/O completion, snapshot throttling bypass, and state-sector update ordering.
