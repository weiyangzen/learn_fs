# File Research: sources/os/bsd/dragonflybsd/sys/vfs/hammer/hammer_io.c

## Purpose
Implements HAMMER’s low-level I/O primitives, buffer-cache association rules, dirty tracking, write ordering hooks, and direct data I/O paths.

## Key Elements
- Defines the modified-I/O red-black tree ordering for volume/buffer dirty lists.
- Initializes and classifies `hammer_io` objects by HAMMER zone.
- Manages passive association between kernel `struct buf` objects and HAMMER volume/buffer structures.
- Provides `hammer_io_read()`, `hammer_io_new()`, `hammer_io_release()`, and `hammer_io_flush()` for loading, creating, releasing, and explicitly flushing backing buffers.
- Tracks dirty metadata/data/undo/volume buffers through `volu_root`, `meta_root`, `undo_root`, `data_root`, and `lose_root`.
- Generates undo records before modifying volume or buffer on-disk bytes via `hammer_modify_volume()` and `hammer_modify_buffer()`.
- Installs `hammer_bioops` callbacks to control kernel writeback, completion, deallocation, and dependency checks.
- Implements direct frontend vnode read/write helpers for large data records, including CRC verification, indirect read mode, async direct-write completion, stale alias invalidation, and device flush commands.

## Dependencies
Uses DragonFlyBSD buffer/bio/vnode APIs from `<sys/buf2.h>` and HAMMER internals from `hammer.h`: blockmap lookup, volume lookup, buffer synchronization/deletion, undo generation, CRC helpers, inode scanning, and flusher/device flush state.

## Behavior/Risks
Metadata and volume buffers are not allowed to be written by ordinary kernel writeback; HAMMER’s flusher must explicitly write them. Data and undo buffers may be released to kernel writeback under controlled conditions. The file is concurrency-sensitive: correctness depends on `io_token`, reference/interlock state, `B_LOCKED`, `modify_refs`, and careful passive buffer disassociation. Direct I/O paths must invalidate or sync aliases so reblocking, mirroring, and frontend vnode buffers do not observe stale data.
