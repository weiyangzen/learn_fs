# File Research: sources/windows/winbtrfs/src/calcthread.c

## Role

`calcthread.c` implements the driver calculation worker system for per-sector checksums and compression/decompression jobs.

## Main Components

- `calc_thread_main(device_extension* Vcb, calc_job* cj)` drains either one targeted job or the global calculation queue.
- `do_calc_job` creates a stack-allocated checksum job over a number of sectors, queues it, helps process it synchronously, and waits for completion.
- `add_calc_job_decomp` allocates a heap job for one zlib/lzo/zstd decompression operation.
- `add_calc_job_comp` allocates a heap job for one zlib/lzo/zstd compression operation.
- `calc_thread` is the system-thread routine that waits on `Vcb->calcthreads.event`, drains queued jobs, honors `thread->quit`, and signals `thread->finished`.

## Job Types

Checksum jobs:

- `calc_thread_crc32c`: stores bitwise-not CRC32C of one sector.
- `calc_thread_xxhash`: stores `XXH64` of one sector.
- `calc_thread_sha256`: calls `calc_sha256`.
- `calc_thread_blake2`: calls `blake2b` with `BLAKE2_HASH_SIZE`.

Compression jobs:

- Decompression: zlib, LZO, ZSTD.
- Compression: zlib, LZO, ZSTD, using mount-level compression options for levels.

## Synchronization

- The queue is protected by `Vcb->calcthreads.spinlock`.
- Each `calc_job` has `left` and `not_started` counters plus a completion event.
- Jobs are removed from the queue when `not_started` reaches zero.
- `InterlockedDecrement(&cj2->left)` signals the job event when all units finish.
- The caller can run `calc_thread_main` directly after enqueueing. This makes checksum jobs partly work-conserving: the submitting thread helps process its own work before blocking.

## Dependencies

- Includes `btrfs_drv.h`, ZSTD's `xxhash.h`, and `crc32c.h`.
- Calls codec functions declared in `btrfs_drv.h`: `zlib_decompress`, `lzo_decompress`, `zstd_decompress`, `zlib_compress`, `lzo_compress`, `zstd_compress`.
- Uses `Vcb->superblock.sector_size`, `Vcb->csum_size`, and `Vcb->options` for job sizing and compression levels.

## Research Notes

- Heap `calc_job` allocations are nonpaged and ownership is passed to the caller, which waits and frees them after completion.
- `calc_thread` pins each worker to an affinity bit derived from `thread->number`.
- The event is set and immediately cleared while holding the spinlock when jobs are enqueued; worker threads wait on that event and then drain all available work.
- Error paths record `cj2->Status` for compression/decompression jobs and log failures.
