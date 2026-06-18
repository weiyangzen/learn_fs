# sources/test-tools/stress-ng/stress-null.c

## Purpose
`stress-null.c` implements the `null` stressor for `/dev/null`. It benchmarks or stresses writes to `/dev/null` and, unless `--null-write` is selected, also exercises miscellaneous operations such as `lseek`, `fcntl`, `ioctl`, `fallocate`, `fdatasync`, and Linux mmap-related paths.

## Important APIs, Types, and Functions
The exported `stress_null_info` registers a `CLASS_DEV | CLASS_MEMORY | CLASS_OS` stressor with `VERIFY_ALWAYS` and the `null-write` boolean option. `stress_null()` is the entry point. It uses `open("/dev/null", O_RDWR)`, `write`, `lseek`, `shim_fallocate`, `shim_fdatasync`, `fcntl(F_GETFL/F_SETFL)`, optional `ioctl(FIGETBSZ/FIONREAD)`, and Linux-only `mmap`, `msync`, and `munmap`.

## Control Flow
The stressor opens `/dev/null`, fills a 4096-byte aligned buffer, waits for synchronized start, and enters either write-only or mixed-operation mode. In write-only mode it writes the buffer until the run stops, tracking bytes and duration for throughput. In mixed mode it periodically times writes for metrics while also seeking to start/end/random offsets, issuing intentionally invalid fallocate/fdatasync-style operations for `/dev/null`, toggling selected file status flags, probing ioctls, and occasionally mapping an anonymous writable page using `/dev/null` as the fd argument while randomizing the offset. Each successful loop increments the bogo counter.

## State and Persistence
The only external object is the `/dev/null` file descriptor, closed before return. File status flags are restored after randomized `F_SETFL` changes when `F_GETFL` succeeds. Mapped pages are anonymous/private and unmapped immediately. The durable state is limited to metrics stored in stress-ng shared memory.

## Dependencies and Integration Points
The stressor depends on standard POSIX file APIs and optional Linux filesystem ioctl definitions. It uses stress-ng shims for memory, fallocate, fdatasync, msync, random values, logging, process states, sync start, bogo counters, and metrics. Unlike many stressors, there is no compile-time unimplemented fallback because `/dev/null` and the core APIs are assumed available enough for the baseline target.

## Risks
Some operations are intentionally invalid for `/dev/null`, so errno variance must remain non-fatal where ignored. The mixed mode measures only sampled write iterations to avoid timing every operation, so reported throughput is approximate. The Linux mmap call uses `MAP_PRIVATE | MAP_ANONYMOUS` with a file descriptor and randomized offset; this is unusual but should ignore the fd due to `MAP_ANONYMOUS` on Linux. Systems without `/dev/null` or with nonstandard semantics fail early.

## Test Signals
Run both `--null 1 --timeout 1 --metrics` and `--null 1 --null-write --timeout 1 --metrics`. Verify clean handling of ignored invalid operations, metric emission for MB/s write rate, and no descriptor leaks. Platform tests should cover builds with and without optional ioctl constants.
