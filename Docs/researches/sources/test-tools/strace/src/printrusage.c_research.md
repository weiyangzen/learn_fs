# sources/test-tools/strace/src/printrusage.c

Purpose: MPERS-aware printer for `struct rusage` returned by `getrusage` and related syscalls.

Important APIs/types/functions: `printrusage` prints user/system time and all resource counters; Alpha additionally defines `printrusage32` with `timeval32_t`.

Control flow: fetches a `kernel_rusage_t` from tracee memory. Always prints `ru_utime` and `ru_stime` through timeval printers; in abbrev mode emits `...` for the remaining counters, otherwise prints RSS, faults, swaps, block I/O, IPC, signals, and context-switch counts.

State and persistence: stateless stack-local decode.

Dependencies/integration: uses `kernel_rusage.h`, MPERS, `print_struct_timeval`, and Alpha timeval32 helpers. Called from `resource.c` getrusage decoders.

Risks: ABI layout differences by personality/Alpha can corrupt field interpretation. Abbrev behavior is intentional and should not be mistaken for incomplete decoding.

Test signals: `getrusage` and `wait4` style tests in full and abbrev modes, invalid pointer behavior, and Alpha personality build coverage.
