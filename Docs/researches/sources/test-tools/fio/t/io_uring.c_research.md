# sources/test-tools/fio/t/io_uring.c

## Purpose
Standalone fio-adjacent benchmark and exerciser for Linux `io_uring`, optional legacy libaio, synchronous `preadv2`, and NVMe passthrough read commands. It stresses submission/completion behavior, registered buffers/files/rings, SQPOLL, IOPOLL, restrictions, NUMA placement, hugepage buffers, vectored I/O, and latency percentile reporting.

## Important APIs, Types, and Functions
`struct submitter` is the per-thread coordinator with ring mappings, files, buffers, counters, latency buckets, and optional aio context. `struct file` tracks max size, offset, pending I/O, fixed file ID, and NVMe namespace metadata. Ring setup uses `io_uring_setup()`, `setup_ring()`, `io_uring_register_buffers()`, `io_uring_register_files()`, `io_uring_register_ring()`, and `io_uring_register_restrictions()`. Fast paths include `prep_more_ios_uring()`, `init_io()`, `init_io_pt()`, `reap_events_uring()`, `reap_events_uring_pt()`, `submitter_uring_fn()`, `submitter_aio_fn()`, and `submitter_sync_fn()`. Latency support uses `plat_val_to_idx()`, `calculate_clat_percentiles()`, and `show_clat_percentiles()`.

## Control Flow
`main()` parses many single-letter options, opens target files/devices, distributes them across submitter threads, optionally maps a hugetlbfs file, then starts one worker thread per submitter. Each worker initializes memory and engine state, keeps queue depth filled up to `depth`, submits in `batch_submit` batches, reaps completions in `batch_complete` batches, updates latency buckets if enabled, and exits when global or per-thread finish is set. The main thread sleeps once per second, prints IOPS/BW/call metrics, enforces optional runtime, handles signals, joins workers, and prints per-thread latency percentiles.

## State and Persistence Behavior
The tool opens targets read-only and does not intentionally write data. It may create a `tsc-rate` file when `-T` is used and may mmap caller-provided hugetlbfs storage. Runtime state includes global finish flags, shared maximum IOPS, per-thread ring mmap regions, allocated I/O buffers, registered resources, and file offsets.

## Dependencies and Integration Points
Depends on Linux `io_uring` syscalls and headers, fio arch/os/rand/minmax helpers, NVMe command definitions, optional libaio, optional libnuma, optional `preadv2`, and block/NVMe device ioctls. It directly exercises kernel interfaces that fio's ioengines also rely on.

## Risks
The program is Linux and feature-level sensitive; many options fail depending on kernel, filesystem, device, privileges, and build macros. Global `sq_ring_mask`/`cq_ring_mask` are shared across submitters and assume compatible rings. Pointer arithmetic on `void *` relies on compiler extensions. Registered resources and mmaps are not comprehensively unwound on every error. Passthrough mode requires `/dev/ngXnY` and read opcode assumptions. Latency buckets require CPU-clock support and enough samples.

## Test Signals
Signals include successful setup for normal, fixed-buffer, fixed-file, SQPOLL, IOPOLL, registered-ring, restricted, vectored, libaio, sync, NUMA, hugetlb, and NVMe passthrough modes; stable IOPS output; no unexpected completion results; and plausible percentile output when stats are enabled.
