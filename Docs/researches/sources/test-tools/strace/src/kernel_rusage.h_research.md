# sources/test-tools/strace/src/kernel_rusage.h

Purpose: defines strace's kernel ABI layout for `struct rusage`.

Important APIs/types/functions: `kernel_rusage_t`, `kernel_old_timeval_t`, and `kernel_long_t` fields for CPU times, RSS, faults, swaps, block I/O, messages, signals, and context switches.

Control flow: header-only typedef consumed by resource-usage decoders.

State and persistence behavior: no state; it describes fetched tracee memory layout.

Dependencies and integration points: includes `kernel_timeval.h`; used by `getrusage`, wait-family, and similar decoders that need kernel-sized long fields.

Risks: all non-time fields depend on `kernel_long_t`, so compat personality sizing is critical. Time fields use `kernel_old_timeval_t`, including sparc64-specific microsecond layout.

Test signals: cover native and compat `getrusage` output, sparc64 layout if available, negative/large counters, and syscall failures with inaccessible result buffers.
