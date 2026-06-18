# File Research: sources/virtualization/spdk/lib/ftl/ftl_core.c

## Purpose
Implements public FTL IO entry points, core poller processing, read/trim flow, free-band selection, global init/fini buffers, and FTL statistics.

## Public IO
- `spdk_ftl_io_size()` returns `sizeof(struct ftl_io)`.
- `spdk_ftl_writev()` and `spdk_ftl_readv()` validate iovecs/LBA counts, require initialized devices, initialize `ftl_io`, and enqueue to the IO channel submission ring.
- `spdk_ftl_unmap()` validates ranges and alignment; aligned unmaps use FTL trim, unaligned user unmaps complete as NOPs.
- `spdk_ftl_get_io_channel()` wraps `spdk_get_io_channel(dev)`.

## Read Path
- Pins L2P pages before reading.
- Groups contiguous LBAs only when they map contiguously within the same storage tier, base or NV cache.
- Invalid/unwritten LBAs are zero-filled.
- On completion, pinned reads verify L2P mappings still match the read addresses; stale reads are retried via `-EAGAIN`.

## Trim Path
- Acquires a trim sequence ID from NV cache.
- Records trim progress in shared superblock state.
- Updates trim bitmap, trim metadata, and trim log, then persists trim log and trim metadata.
- Supports retry behavior under `SPDK_FTL_RETRY_ON_ERROR`.

## Core Poller
`ftl_core_poller()` processes submitted IOs, runs user and GC writers, relocation, NV-cache processing, and L2P processing. During halt it waits for inflight IO, writers, relocation, NV cache, bands, and L2P to become quiescent.

## Statistics
Tracks bdev read/write blocks and errors by stats type; supports async stats retrieval from the FTL core thread.

## Dependencies
Uses SPDK bdev/thread/NVMe status APIs, FTL band/IO/debug/internal/mngt/NV-cache/writer/reloc/L2P modules.
