# File Research: sources/os/darwin/xnu/bsd/vfs/vfs_io_compression_stats.c

## Scope

This file implements optional VFS I/O compression statistics collection. It samples write buffers, LZ4-compresses them in configurable blocks, updates per-vnode compression histograms, records reclaimed vnode stats into a circular store buffer, notifies userspace, and exposes sysctl controls/dumps.

## Public And Internal APIs Covered

- Main sampling entry: `io_compression_stats(buf_t bp)`.
- Reclaim recording: `vnode_iocs_record_and_free(struct vnode *)`.
- Stats updates: `vnode_updateiocompressionblockstats()` and `vnode_updateiocompressionbufferstats()`.
- Sysctls: `vfs.io_compression_stats_enable`, `vfs.io_compression_stats_block_size`, and `vfs.io_compression_dump_stats`.
- Internal helpers allocate/free per-CPU buffers, compress blocks/buffers, bucket sizes/compressibility, construct store-buffer entries, notify userspace, and iterate live vnodes.

## Control Flow And Behavior

Enabling via sysctl allocates per-CPU LZ4 scratch buffers, per-CPU destination buffers sized by block size, the circular store buffer, and a path scratch buffer. Disabling frees all of them. Changing block size while enabled reallocates buffers; allocation failure disables stats.

`io_compression_stats()` ignores reads and zero-length buffers. For writes, it takes the stats lock opportunistically, maps the buffer, compresses it by blocks using per-CPU scratch/destination buffers with preemption disabled, updates per-vnode block and buffer histograms, emits a KDBG tracepoint, unlocks, and unmaps.

When a vnode with stats is reclaimed, `vnode_iocs_record_and_free()` tries to append a path plus stats snapshot into the store buffer, wraps at buffer end, optionally notifies a host special port, then clears and frees the vnode stats regardless of recording success.

Dump sysctl supports live vnode iteration or store-buffer reads. Store-buffer reads can be read-only or mark the current position as consumed.

## State And Data Structures

- Globals: `io_compression_stats_enable`, `io_compression_stats_block_size`, per-CPU scratch/compression buffers, `per_cpu_buf_size`, `vnpath_scratch_buf`, and `iocs_store_buffer`.
- Locks: `io_compression_stats_lock` protects enable/block-size/buffer lifetime; `iocs_store_buffer_lock` protects archive buffer state.
- Per-vnode stats are allocated from `io_compression_stats_zone` and stored on `vp->io_compression_stats`.

## Dependencies

Depends on buffer mapping, vnode internals, LZ4 raw encoder, Mach host notification port APIs, sysctl, vfs/vnode iteration, KDBG, per-CPU storage, atomic counters, and kernel allocation APIs.

## Risks And Invariants

- Compression runs with preemption disabled while using per-CPU buffers.
- `io_compression_stats()` uses try-locking to avoid blocking I/O paths during sysctl reconfiguration.
- `get_buffer_compressibility_bucket()` uses `log2down(saved_space_pc)`; a zero saved-space percentage is a sensitive input for `__builtin_clz`.
- `vnpath_scratch_buf` is global and protected only by store-buffer/live dump call paths; concurrent path construction relies on higher-level serialization.
- `vnode_updateiocompressionbufferstats()` assumes block stats allocation happened first.
- Store-buffer copyout must handle wraparound and caller-provided buffer size precisely.
