<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-aiol.c -->
# sources/test-tools/stress-ng/stress-aiol.c

Purpose: `stress-aiol.c` implements the `aiol` stressor for the Linux native AIO syscall ABI. It stresses `io_setup`, `io_submit`, `io_getevents`/`io_pgetevents`, `io_cancel`, vector I/O opcodes, poll/fsync opcodes, and invalid syscall argument paths.

Important APIs/types/functions: `stress_aiol_info_t` owns aligned I/O buffers, `struct iocb` arrays, `struct io_event` arrays, iocb pointer arrays, per-request file descriptors, `iovec` entries, write results, the AIO context, and completion count. Shim wrappers call `__NR_io_setup`, `io_destroy`, `io_submit`, `io_getevents`, optional `io_cancel`, and optional `io_pgetevents` directly through `syscall()`. `stress_aiol_fill_buffer()` and `stress_aiol_check_buffer()` provide deterministic data verification. `stress_aiol_submit()` handles `EAGAIN` retries and optional `EINVAL` tolerance; `stress_aiol_wait()` drains completions with short absolute timeouts.

Control flow: `stress_aiol()` resolves `aiol-requests`, caps it against `/proc/sys/fs/aio-max-nr` divided by instances, allocates all arrays, deliberately tries invalid `io_setup(0)`, creates a Linux AIO context, opens a temporary file with `O_DIRECT` fallback, opens many descriptors to the same file, then enters the synchronized run loop. Each iteration submits and waits for async `PWRITE`, validates later `PREAD` data where the prior write succeeded, submits `PWRITEV` and `PREADV`, periodically exercises invalid `io_cancel`, `io_destroy`, `io_getevents`, `io_setup`, and `io_submit` calls, optionally submits invalid `IO_CMD_POLL`, and periodically tests `IO_CMD_FDSYNC` or `IO_CMD_FSYNC`.

State and persistence behavior: persistent filesystem state is a temp file unlinked after descriptors are opened and a temp directory removed on cleanup. Kernel state is the AIO context and outstanding requests. Local state includes per-request buffers, event results, write status, completion counters, and static retry suppression for unsupported `io_pgetevents` and sync opcodes.

Dependencies and integration points: the implementation is Linux-only through syscall numbers plus `libaio.h`, `clock_gettime`, optional `poll.h`, stress-ng temp file helpers, process states, sync barriers, memory allocation helpers, filesystem hints, random helpers, and metrics. It registers `aiol-requests`, `VERIFY_ALWAYS`, and an unimplemented reason when libaio/syscall support is missing.

Risks: buffer validation includes a suspicious bounds guard, `if (bufptr >= info.buffer + BUFFER_SZ) continue;`, which rejects buffers beyond the first 4 KB slot rather than beyond the full allocation; this means most read completions can skip verification. Resource capping relies on parsing one byte from `/proc/sys/fs/aio-max-nr`, so larger values can fall back to the default guess. Direct I/O alignment, filesystem support, and kernel opcode support vary widely.

Test signals: run on kernels with and without `io_pgetevents`, with small and large `aiol-requests`, on filesystems that reject `O_DIRECT`, under low `aio-max-nr`, and with verify enabled to catch read/write mismatches. Metrics are `async I/O events completed` and `async I/O events completed per sec`.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-aiol.c -->
