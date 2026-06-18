# File Research: sources/virtualization/spdk/module/bdev/malloc/bdev_malloc.c

## Purpose
Implements SPDK's in-memory malloc bdev. It allocates DMA-capable backing memory, supports optional metadata and DIF/DIX protection information, uses the accel framework for data movement, and exposes read/write/flush/reset/unmap/write-zeroes/zcopy/abort/compare/copy operations.

## Main Entry Points
- `create_malloc_disk()` validates options, allocates backing memory and optional metadata memory, initializes PI if requested, registers the bdev, and inserts it into `g_malloc_disks`.
- `delete_malloc_disk()` unregisters a named malloc bdev.
- `bdev_malloc_submit_request()` dispatches each bdev I/O type.
- Module init/fini register/unregister the shared I/O device used for malloc channels.

## Internal Mechanics
Each `malloc_disk` owns the public bdev plus `malloc_buf` and optional separate metadata buffer. Each channel owns an accel I/O channel and a completion poller. Synchronous completions are queued in `completed_tasks` and drained by `malloc_completion_poller()`.

Reads, writes, compares, copies, unmaps, and write-zeroes are implemented with accel copy/compare/fill operations. Read with a null iov base maps the caller directly to the backing buffer and optional metadata buffer, then completes without copying. ZCOPY start similarly exposes the backing buffer. Abort always fails.

Protection information support verifies incoming data on writes when metadata is visible, verifies stored data before hidden-metadata reads, verifies read buffers after reads with visible metadata, and regenerates PI after unmap/write-zeroes. Initial PI is generated over the full disk when DIF is enabled. Supported metadata sizes are 0, 8, 16, 32, 64, and 128 bytes.

Config JSON emits replayable `bdev_malloc_create` entries with geometry, UUID, optimal boundary, metadata, DIF, PI format, and NUMA ID. Memory domain support is broad when DIF is disabled and disabled when DIF is enabled.

## Dependencies
Uses SPDK bdev module APIs, DMA allocation, accel framework, DIF/DIX helpers, endian/string/log utilities, memory domains, pollers, and NUMA enumeration.

## Risks and Notes
Large allocations are pinned DMA memory and can fail for size, alignment, NUMA, or hugepage availability. `physical_block_size` must be 512-byte aligned but is not defaulted in this file if callers pass zero. Accel sequence failure handling intentionally maps sequence `-ENOMEM` to `-EFAULT` at finish to prevent bdev-layer retry of an already failed sequence.
