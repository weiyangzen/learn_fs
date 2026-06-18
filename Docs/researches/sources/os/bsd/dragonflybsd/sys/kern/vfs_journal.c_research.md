# File Research: sources/os/bsd/dragonflybsd/sys/kern/vfs_journal.c

## Summary
Provides the low-level journaling transport and record serialization machinery used by `vfs_jops.c`: FIFO reservation, worker threads, stream commit/abort, subrecord nesting, and helpers for serializing VFS objects.

## Main Responsibilities
- Creates/destroys journal writer and optional full-duplex reader threads.
- Manages the per-journal circular memory FIFO.
- Reserves, extends, pads, commits, and aborts raw journal stream records.
- Builds nested logical journal records with `jrecord_*` APIs.
- Serializes paths, vnode attributes, credentials, vnode references, page lists, UIOs, and preimage file data.

## Important Behavior
Records are first reserved as incomplete so the writer thread cannot flush past them. Commit writes trailers and sets begin magic last with memory barriers. If a record cannot grow in place, `journal_extend()` commits the current segment and continues the logical stream in a new raw record.

The writer thread batches complete records and writes them to `jo->fp`. In non-full-duplex mode it treats written bytes as acknowledged. In full-duplex mode the reader thread consumes acknowledgement records and advances `xindex`, allowing restart from the last acknowledged point.

`jrecord_push()` and `jrecord_pop()` support nested records even when FIFO pressure makes parent pointers stale; the stream format tolerates unknown nested record sizes in that case.

## Risks
The file contains many forward-looking XXXs: partial write/nonblocking I/O handling, failure notification, checksum disabled, permanent versus temporary failure policy, SMP thread teardown interlocks, and acknowledgement protocol maturity. `copyin()`/XIO copy paths inside `jrecord_data()` do not propagate copy errors to callers.
