# sources/test-tools/fio/engines/io_uring.c

## Purpose
Implements fio's Linux `io_uring` engines: `io_uring` for normal read/write/sync/trim SQEs and `io_uring_cmd` for NVMe passthrough commands. It is the high-performance async path for block/file workloads and the integration point for NVMe protection information, zoned namespace helpers, FDP reclaim-unit-handle queries, mixed NVMe write modes, registered files, fixed buffers, SQ polling, and command priority.

## Important APIs, Types, And Functions
Core state lives in `struct ioring_data`, which owns the ring fd, mapped SQ/CQ rings, SQEs, iovec/fixed-buffer tables, per-`io_u` index table, optional metadata buffers, command-priority state, NVMe DSM buffers, and `nvme_cmd_ext_io_opts`. `struct ioring_options` exposes engine options including `hipri`, `fixedbufs`, `registerfiles`, `sqthread_poll`, `nowait`, `force_async`, `md_per_io_size`, PI tag/check settings, `readfua`, `writefua`, `write_mode`, `verify_mode`, and `cmd_type`.

Important functions are `fio_ioring_init()`, `fio_ioring_post_init()`, `fio_ioring_queue_init()`, `fio_ioring_mmap()`, `fio_ioring_prep()`, `fio_ioring_cmd_prep()`, `fio_ioring_queue()`, `fio_ioring_commit()`, `fio_ioring_getevents()`, `fio_ioring_event()`, and `fio_ioring_cmd_event()`. File and NVMe setup are handled by `fio_ioring_open_file()`, `fio_ioring_cmd_open_file()`, `fio_ioring_open_nvme()`, `fio_ioring_cmd_get_file_size()`, and PI helpers such as `fio_get_pi_info()`.

## Control Flow
Initialization allocates per-thread state, rounds internal ring depth to a power of two, configures metadata/PI buffers, initializes command priority, allocates NVMe DSM ranges, and configures io_uring features. `post_init` attaches all `io_u` objects to iovecs, creates the ring with feature fallback for newer setup flags, optionally registers buffers and files, probes for non-vectored opcode support, and mmaps SQ/CQ state.

For normal `io_uring`, `prep` fills an SQE for read/write, fsync/sync-file-range, or discard via `IORING_OP_URING_CMD`. For `io_uring_cmd`, `prep` builds NVMe command structures through `fio_nvme_uring_cmd_prep()`, optionally converts verification reads to compare commands, and randomly selects a write opcode for mixed `write_mode` ratios. `queue` stores the SQE index in the SQ ring, applies command priority and PI generation, and has a special busy path that prevents fsynced verification flushes from racing in-flight NVMe writes. `commit` submits queued SQEs with `io_uring_enter()` or wakes SQPOLL. Completion reaping advances CQ heads, maps CQEs back to `io_u`, and translates short/error/device-specific status.

## State And Persistence
State is per fio thread except for the global `enter_flags`, which is augmented if the kernel advertises `IORING_FEAT_NO_IOWAIT`. Registered files keep `fio_file->fd` logically closed while storing real descriptors in `ld->fds`. File engine data stores NVMe namespace/metadata information. Persistent media state can be changed by write, DSM/trim, write zeroes, write uncorrectable, flush, and zoned reset/finish/move operations.

## Dependencies And Integration Points
Depends on Linux io_uring syscalls/UAPI, fio core `ioengine_ops`, `cmdprio`, `verify`, `zbd`, block-zoned helpers, and local NVMe helpers from `nvme.c/.h`. The normal engine delegates zoned operations to `blkzoned_*`; the command engine delegates to `fio_nvme_*`. It integrates with fio buffer registration, file registration, command priority, verify modes, FDP, atomic writes, and error-detail reporting.

## Risks
Ring memory is manually mapped and indexed; `io_uring_cmd` doubles SQE/CQE slot addressing and must keep index math exact. CQ head is advanced before CQE data is consumed, relying on queue-depth sizing. `enter_flags` is process-global, so feature discovery affects later threads. Metadata/PI paths require strict alignment and block-size validation. NVMe FUA and fsynced verification are explicitly incompatible. Async trim fallback depends on `async_trim_fail`; zbd trim is marked synchronous for command engine. Kernel feature fallback paths should be tested on old and new kernels.

## Test Signals
Useful tests include normal read/write with vectored and non-vectored paths, fixed buffers, registered files, SQPOLL, `nowait`, `uncached`, command priority, sync and trim fallback, `io_uring_cmd` NVMe read/write/compare/write-zeroes/write-uncor mixes, FUA options, PI generation/verification with 16-byte and 64-byte guards, invalid metadata/block-size combinations, zoned namespace report/reset/finish/move, FDP RUH fetch, and kernel feature fallback for setup flags.
