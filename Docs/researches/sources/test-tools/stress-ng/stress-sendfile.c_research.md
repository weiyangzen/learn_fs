# sources/test-tools/stress-ng/stress-sendfile.c

Purpose: implements the `sendfile` stressor, copying a preallocated temporary file to `/dev/null` using the kernel `sendfile` path and periodically probing invalid fd, offset, size, and mode combinations.

Important APIs/types/functions: `stress_sendfile`, `sendfile`, `shim_posix_fallocate`, `shim_fallocate`, `stress_fs_temp_dir_make_args`, `stress_fs_temp_filename_args`, `stress_fs_bad_fd_get`, `stress_metrics_set`, `open`, `close`, and `/dev/null`.

Control flow: the worker resolves `sendfile-size`, creates a temp directory and file, allocates the requested size, reopens it read-only, unlinks it, opens `/dev/null` writable, synchronizes start, and loops calling `sendfile(fdout, fdin, &offset, sz)`. Most calls are fast; every 1001st successful call contributes timing/byte metrics. Every 256 iterations it exercises invalid destination/source descriptors, negative offset, `(size_t)-1` size, zero-byte no-op, read-only destination, write-only source, and truncated reads.

State and persistence behavior: all durable state is a temporary unlinked file and `/dev/null` fd; temp directories are removed at exit. Metrics accumulate measured bytes/time for sampled calls and export MB/sec.

Dependencies and integration points: registered as `CLASS_PIPE_IO | CLASS_OS`, always verify, with `sendfile-size` option. It requires `<sys/sendfile.h>`, `sendfile`, and a glibc feature gate; otherwise it reports unimplemented.

Risks and test signals: expected skips include fallocate interruption/resource failure and runtime `ENOSYS`. Real failures are unexpected `sendfile` errors, failure to close descriptors/remove temp directories, or metrics staying at zero despite successful copies.
