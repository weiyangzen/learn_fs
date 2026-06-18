# sources/test-tools/stress-ng/stress-copy-file.c

## Purpose
This stressor exercises Linux `copy_file_range()` behavior through stress-ng's filesystem workload framework. It creates a temporary source file and destination file, writes random data into source ranges, copies fixed-size chunks between randomized offsets, optionally verifies copied bytes, and records copy throughput. When the build lacks `copy_file_range()` support it registers an unimplemented stressor with the same option/help metadata.

## Important APIs, Types, And Functions
The exported object is `stress_copy_file_info`, classified as filesystem and OS work with optional verification. `opts` exposes `copy-file-bytes` with minimum, maximum, maximize, and minimize handling. `stress_copy_file_seek64()` wraps `lseek64()` or guarded `lseek()` fallback. `stress_copy_file_fill()` fills a file region with a repeated random byte. `stress_copy_file_range_verify()` compares source and destination windows in 4 KiB buffers. `stress_copy_file()` owns setup, the copy loop, error classification, metrics, and cleanup.

## Control Flow
`stress_copy_file()` normalizes the requested total bytes across instances, creates a temp directory, opens an unlinked original file and unlinked copy file, truncates the input, and queries optional `pathconf()` transfer parameters. After the sync barrier it repeatedly selects random source and destination offsets, writes `DEFAULT_COPY_FILE_SIZE` bytes to the input, times `shim_copy_file_range()`, verifies the copy when `--verify` is active, deliberately calls `copy_file_range()` with bad descriptors and flags, fsyncs the output, and increments bogo operations. `ENOSYS` and filesystem `EINVAL` are treated as skip/no-resource cases; ordinary failures are reported.

## State And Persistence
State is local to the worker except for stress-ng global options, metrics, temporary filesystem space, and process state markers. Files are unlinked soon after opening, so the persistent artifact is temporary storage pressure rather than durable names. Metrics record harmonic-mean MB/s based on successful copied bytes and measured syscall duration.

## Dependencies And Integration Points
This file depends on stress-ng filesystem helpers, random MWC generators, shim syscall wrappers, bogo/metrics APIs, and compile-time `HAVE_COPY_FILE_RANGE`. It integrates with the option parser through `OPT_copy_file_bytes` and with the global verify/minimize/maximize flags.

## Risks
Large `copy-file-bytes` values can consume substantial temporary filesystem capacity across instances. Filesystems differ in `copy_file_range()` support, so `EINVAL` may indicate unsupported kernel splice paths rather than a test failure. Verification only checks the copied window and relies on correct offset restoration. The fallback seek path must reject offsets too large for `off_t` to avoid truncation.

## Test Signals
Useful signals are successful runs on filesystems with native copy support, graceful `EXIT_NO_RESOURCE` on unsupported kernels/filesystems, accurate verify-mode comparisons, cleanup of temporary directories, and a nonzero "MB per sec copy rate" metric. Fault paths should cover `ENOSPC`, bad descriptor calls, bad flag calls, and per-instance byte scaling.
