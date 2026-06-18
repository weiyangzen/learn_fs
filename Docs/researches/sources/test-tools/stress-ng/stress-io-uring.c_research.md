# sources/test-tools/stress-ng/stress-io-uring.c

## Purpose
`stress-io-uring.c` stresses Linux io_uring setup, submission, completion, and many available opcodes against a small temporary file and mapped iovec buffers. It is run inside an OOM-isolated child.

## Important APIs, Types, And Functions
Options are `io-uring-entries`, `io-uring-rand`, and `io-uring-ops`. `stress_io_uring_file_t` stores file fds, path, iovecs, block sizing, and file size. `stress_io_uring_submit_t` stores SQ/CQ ring mappings, SQEs, fd, and sizes. `shim_io_uring_setup()` and `shim_io_uring_enter()` wrap raw syscalls. `stress_setup_io_uring()` creates rings and mmaps SQ/CQ/SQE areas. `stress_io_uring_submit()` fills an SQE via an opcode-specific setup function, advances the SQ tail, calls `io_uring_enter`, and increments bogo ops. `stress_io_uring_complete()` consumes CQEs and classifies tolerated errors. Opcode setup functions cover read/write, vectored I/O, fsync, nop, fallocate, fadvise, close, madvise, statx, sync_file_range, xattr, ftruncate, and async cancel when compiled.

## Control Flow
The child chooses entries based on CPU count or options, maps iovec structures and buffers, creates a temp directory/file path, sets up io_uring, waits at the barrier, initializes per-opcode user data as supported, then loops. Each iteration opens/truncates the temp file, optionally opens an `O_PATH` fd for statx, submits all or random opcode setup entries that remain supported, drains completions, periodically reads fdinfo, closes fds, and repeats. Cleanup cancels pending read/write ops when available, closes/unmaps rings, unmaps iovecs, unlinks the file, and removes the temp directory.

## State And Persistence
State includes mmap-backed ring buffers, mmap-backed iovec buffers, temp file path/fds, supported flags per opcode, and global `io_uring_rand`. Temporary files are removed.

## Dependencies And Integration Points
Requires Linux io_uring headers, raw syscall numbers, ring offset macros, `posix_memalign`, at least one supported opcode macro, stress-ng mmap/temp/OOM helpers, optional xattr/statx/madvise/fadvise support, and memory barriers.

## Risks
Kernel io_uring restrictions, seccomp, `EPERM`, missing opcodes, or low memory must skip. Ring-tail manipulation is low-level and sensitive to memory barriers. Some completion errors are intentionally tolerated; over-broad tolerance can hide regressions, while under-tolerance causes false failures on filesystem/kernel differences. Static buffers in xattr/statx setup are shared per process.

## Test Signals
Signals include correct skip on `ENOSYS`, `EPERM`, or oversized entries, successful ring mmap/unmap, opcode support downgrades on `EOPNOTSUPP`, no ring stalls under randomized order, clean temp cleanup, and bogo progress through submissions.
