# File Research: sources/os/bsd/openbsd-src/sbin/dump/tape.c

## Purpose
Handles dump output buffering, tape/file writes, media changes, checkpoint/rewrite recovery, and concurrent disk-read/tape-write slave processes.

## Key Behavior
- `alloctape()` allocates per-slave request buffers and aligned tape buffers sized by `ntrec * TP_BSIZE`.
- `writerec()` queues special/header records into the current tape block.
- `dumpblock()` queues filesystem data blocks as disk read requests translated to device blocks.
- `flushtape()` sends request batches to slaves, receives write results, detects EOT/short writes, advances tape counters, starts new media when size limits are reached, and updates estimates.
- `startnewtape()` implements checkpointing by forking. The parent preserves state and reforks on `X_REWRITE`; the child opens the output and continues.
- Supports comma-separated output device lists for successive volumes.
- `enslave()` forks three slave processes connected by socketpairs. Slaves coordinate write turns through SIGUSR2.
- `doslave()` reopens the disk, reads requested blocks into tape buffers, waits for its turn, writes to local or remote output, and reports byte counts to the master.
- `rollforward()` replays buffered records after EOT so the next volume starts at a coherent point.
- `trewind()` drains slave responses, closes/waits for slaves, closes/reopens tape devices as needed, and handles remote close/open checks.
- `tperror()`, `sigpipe()`, `dumpabort()`, and `Exit()` handle write failures and abort paths.
- `do_stats()` and `statussig()` report per-volume timing and transfer rate.

## Notes
This is the program’s most complex operational module. It combines historical tape behavior, process checkpointing, signal coordination, and partial-write/EOT recovery.
