# File Research: sources/os/bsd/freebsd-src/sys/kern/subr_disk.c

## Purpose
Provides disk-related utility routines: formatted disk transfer error reporting and a BIO queue implementation with seek sorting and barrier semantics.

## Key Elements
- Debug sysctl: `debug.bioq_batchsize`.
- Error formatter: `disk_err()`.
- Queue lifecycle: `bioq_init()`.
- Queue operations: `bioq_insert_head()`, `bioq_insert_tail()`, `bioq_first()`, `bioq_takefirst()`, `bioq_remove()`, `bioq_flush()`.
- Sort helper: `bioq_disksort()`.

## Behavior
`disk_err()` prints device or disk name, BIO command, and filesystem block range. It handles unknown devices, single-block transfers, and a known completed block offset.

The BIO queue uses a TAILQ plus metadata:
- `last_offset` models current disk head position.
- `insert_point` acts as a barrier for later sorted inserts.
- `total` counts queued BIOs.
- `batched` limits long sorted batches.

`bioq_disksort()` only sorts read, write, and delete BIOs without `BIO_ORDERED`. Ordered or non-offset commands go to the tail and create ordering barriers. Sorting uses unsigned offset distance from `last_offset`, preserving elevator-style scan ordering.

## Research Notes
Direct queue operations intentionally alter future sorting behavior. `bioq_insert_tail()` creates a barrier, while `bioq_insert_head()` updates `last_offset` so later sorted requests stay behind the inserted head request.
