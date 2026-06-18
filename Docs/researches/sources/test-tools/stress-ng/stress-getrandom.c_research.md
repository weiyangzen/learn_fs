<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-getrandom.c -->
# sources/test-tools/stress-ng/stress-getrandom.c Research

Purpose: implements `getrandom`, an OS/CPU stressor that reads kernel random data via `getrandom()` and, when available, `getentropy()`.

Important APIs/types/functions: `stress_getrandom_supported()` probes `shim_getrandom()` and skips ENOSYS systems. `getrandom_flags_t` maps flag values to names. `getrandom_flags[]` includes zero flags, Linux nonblocking/random/insecure combinations when available, intentionally invalid combinations such as insecure+random, and `~0U`. `stress_getrandom()` performs reads, handles expected transient/invalid errors, accounts bytes, and emits bit-rate metrics.

Control flow: after synchronization, the stressor loops over all flag entries while work continues. For each flag it calls `shim_getrandom()` into a stack buffer sized 256 bytes on OpenBSD/macOS or 8192 bytes elsewhere. `EAGAIN`, `EINTR`, and `EINVAL` are accepted for nonblocking or invalid flag cases. ENOSYS becomes `EXIT_NOT_IMPLEMENTED`; other errors are failures. Successful reads add returned byte counts. `getentropy(buffer, 1)` is also exercised when available. Bogo operations increment per flag iteration, and exit metrics report getrandom bits/sec.

State and persistence: all random data is stack-local and discarded. Only local duration/byte counters persist for the run. No files or global state are modified.

Dependencies and integration: depends on platform support for OpenBSD, Apple, FreeBSD, or Linux `__NR_getrandom`; optional `<linux/random.h>` flags; stress-ng syscall shims, support hooks, sync/state, and metrics.

Risks: flag semantics vary by kernel and libc. Invalid flag combinations are intentionally tolerated via `EINVAL`. `GRND_RANDOM` or early-boot entropy behavior can block or return `EAGAIN` depending on flags and OS. Large buffer sizes may change syscall cost across platforms.

Test signals: expected output is a getrandom bits/sec metric and no unexpected error logs. Test with Linux kernels supporting and lacking `GRND_INSECURE`, non-Linux supported platforms, and environments with constrained entropy or syscall filtering.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-getrandom.c -->
