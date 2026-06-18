# sources/test-tools/strace/src/print_timeval64.c

Purpose: Thin constructor for the 64-bit timeval printer variant.

Important APIs/types/functions: defines `timeval_t` as `kernel_timeval64_t` and includes `print_timeval.c` with `MPERS_IS_m32` so the generated names target the 64-bit layout while using the common implementation.

Control flow: delegates entirely to `print_timeval.c`.

State and persistence: inherits static string buffer behavior from the common file.

Dependencies/integration: relies on MPERS machinery, `kernel_timeval.h`, and syscall decoders that need `timeval64`-layout output.

Risks: include-based reuse can be confusing during maintenance; the `MPERS_IS_m32` define must correspond to the intended generated personality.

Test signals: time64 timeval syscalls and rusage consumers should decode 64-bit seconds/useconds without falling back to raw addresses.
