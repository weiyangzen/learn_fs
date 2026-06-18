# File Research: sources/windows/reactos/drivers/filesystems/btrfs/calcthread.c

## Purpose

Implements worker-thread execution for CPU-bound Btrfs jobs: sector checksums/hashes and compression/decompression tasks. It supports both background calc threads and synchronous caller-assisted execution.

## Main Functions

- `calc_thread_main(device_extension* Vcb, calc_job* cj)`
- `do_calc_job(device_extension* Vcb, uint8_t* data, uint32_t sectors, void* csum)`
- `add_calc_job_decomp(...)`
- `add_calc_job_comp(...)`
- `calc_thread(void* context)`

## Behavior

`calc_thread_main`:

- Acquires `Vcb->calcthreads.spinlock`.
- Selects either a caller-supplied job or the head of the queued job list.
- For checksum/hash jobs, advances `in` by one sector and `out` by checksum size for each work unit.
- Decrements `not_started`, removes the job from the queue when no units remain, and releases the spinlock.
- Executes the selected work:
  - CRC32C via `calc_crc32c`.
  - XXH64 via `XXH64`.
  - SHA-256 via `calc_sha256`.
  - BLAKE2 via `blake2b`.
  - Zlib/LZO/Zstd decompression via codec functions.
  - Zlib/LZO/Zstd compression via codec functions.
- Decrements `left` atomically and signals the job event when all work units complete.

`do_calc_job`:

- Builds a stack-local `calc_job` for checksum generation across multiple sectors.
- Selects checksum type from `Vcb->superblock.csum_type`.
- Inserts the job into the calc queue.
- Signals calc threads, runs `calc_thread_main` itself to help drain the job, then waits for completion.

`add_calc_job_decomp` and `add_calc_job_comp`:

- Allocate a nonpaged `calc_job`.
- Initialize input/output buffers, lengths, status, event, and type.
- Validate the Btrfs compression type.
- Queue the job and return it to the caller for waiting/freeing.

`calc_thread`:

- References the device object.
- Pins the system thread to `1 << thread->number`.
- Waits on `Vcb->calcthreads.event`, drains queued jobs, and exits when `thread->quit` is set.
- Signals `thread->finished` and terminates.

## Dependencies

- Includes `xxhash.h` and `crc32c.h`.
- Calls compression functions declared in `btrfs_drv.h` and implemented in `compress.c`.
- Calls SHA-256 and BLAKE2 functions declared in `btrfs_drv.h`.
- Uses Windows kernel spinlocks, events, interlocked operations, system threads, and object references.

## Research Notes

- The design lets submitters participate in execution, reducing latency for synchronous checksum/compression work.
- `calc_job` ownership is split: stack-owned for `do_calc_job`, heap-owned for compression/decompression helper APIs.
- The queue counters are protected by spinlock, while completion uses `InterlockedDecrement` plus an event.
- The event is set and immediately cleared when jobs are queued; calc threads wake on the set edge while the job list remains authoritative.
