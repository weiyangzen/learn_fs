<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-aio.c -->
# sources/test-tools/stress-ng/stress-aio.c

Purpose: `stress-aio.c` implements the `aio` stressor, which exercises POSIX asynchronous I/O via `aio_read`, `aio_write`, optional `aio_fsync`, signal notification, cancellation, and temporary-file backed read/write cycling. It is an I/O, interrupt, and OS stressor registered as `stress_aio_info`.

Important APIs/types/functions: the build-gated implementation requires `HAVE_LIB_RT`, `aio.h`, `aio_cancel`, `aio_read`, and `aio_write`. `stress_io_req_t` stores the request slot, last AIO status, `struct aiocb`, a 16-byte buffer, and a signal-delivery count. `aio_fill_buffer()` seeds deterministic data, `aio_signal_handler()` accounts `SIGUSR1` completions through `sigev_value.sival_ptr`, `aio_issue_cancel()` polls `aio_error()` and retries `aio_cancel()`, and `issue_aio_request()`/`issue_aio_sync_request()` initialize `aiocb` objects for read/write/fsync operations.

Control flow: `stress_aio()` reads `aio-requests` or applies maximize/minimize bounds, allocates the request array, creates a per-worker temp directory and file, installs a `SIGUSR1` `SA_SIGINFO` handler, submits initial writes for every slot, waits at the synchronized start barrier, then loops while `stress_continue(args)` is true. Each pass checks `aio_error()`, counts completed or canceled operations, and resubmits read, write, or final-slot fsync work. On hard AIO errors it jumps to cancellation and cleanup.

State and persistence behavior: persistent state is limited to the temporary file and directory, unlinked immediately after opening and removed at deinit. Runtime state lives in `io_reqs`, the process-wide `do_accounting` flag, the installed signal handler, per-request completion counters, and stress-ng metrics. The file descriptor receives a short read/write hint.

Dependencies and integration points: the stressor uses stress-ng option parsing, sync barriers, process-state tracking, temporary filesystem helpers, random selection via `stress_mwc1()`, bogo counters, metrics, and common exit-status mapping. It is exposed through the stressor table with `VERIFY_ALWAYS` and an unimplemented fallback when POSIX AIO support is absent.

Risks: signal accounting is global to the process and depends on `do_accounting` being disabled before cancellation; changes around handler lifetime or multiple stressors sharing `SIGUSR1` can skew metrics. Filesystem-specific `ENOSPC` is silently ignored for writes but other `aio_error()` values fail. Cancellation loops can delay teardown if a request remains `AIO_NOTCANCELED`.

Test signals: useful coverage includes builds with and without librt/AIO support, small and maximum `aio-requests`, filesystems returning `ENOSPC`, interruption during `aio_cancel()`, optional `aio_fsync` paths with `O_SYNC`/`O_DSYNC`, and metrics named `async I/O signals per sec` and `async I/O signals`.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-aio.c -->
