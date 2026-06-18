<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/aio_pgetevents.c -->
## sources/test-tools/strace/tests/aio_pgetevents.c

Purpose: Tests `io_pgetevents` decoding, especially timeout and signal-mask argument structures.

Important APIs/types/functions: Defines fallback `struct __aio_sigset`, helper `sys_io_pgetevents`, uses `NSIG_BYTES`, `sigset_t`, `sigemptyset`, `sigaddset`, `kernel_old_timespec_t`, and AIO setup/submit helpers.

Control flow: Opens `/dev/zero`, creates an AIO context, submits two reads, probes bogus context/min/max with bad events, timeout, and sigset pointers, then prints structured sigmask cases for invalid size, all-signals mask, and `[SYS]` mask with large timeout values.

State and persistence: Temporarily owns an AIO context and allocated buffers; the shown source does not explicitly destroy context before process exit, so kernel cleanup occurs on exit.

Dependencies and integration: Exercises strace decoding for six-argument `io_pgetevents`, old timespecs, signal set rendering, and AIO event pointers.

Risks: Availability is kernel/architecture dependent. Signal set size and names must match the harness `nsig.h` assumptions.

Test signals: Output should show NULL vs pointer decoding for `events`, `timeout`, and `sigmask`, `~[]` for full mask, `[SYS]` for SIGSYS, and clean exit or skip when unsupported.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/aio_pgetevents.c -->
