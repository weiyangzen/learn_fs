# sources/test-tools/strace/src/print_timespec32.c

Purpose: Builds the 32-bit `timespec` printer family by selecting `kernel_timespec32_t` and including `print_timespec.h`.

Important APIs/types/functions: defines `TIMESPEC_T`, `PRINT_TIMESPEC`, `SPRINT_TIMESPEC`, `PRINT_TIMESPEC_UTIME_PAIR`, and `PRINT_ITIMERSPEC` with `32` suffixes, producing `print_timespec32`, `sprint_timespec32`, `print_timespec32_utime_pair`, and `print_itimerspec32`.

Control flow: there is no independent runtime logic; all fetch, printing, utime special-case, and itimerspec behavior comes from `print_timespec.h`.

State and persistence: inherits only the header's formatter static buffer behavior.

Dependencies/integration: includes `defs.h`, `kernel_timespec.h`, sets `TIMESPEC_NSEC` to the 32-bit kernel field `tv_nsec`, and integrates with syscall decoders needing old/compat time ABI layouts.

Risks: ABI correctness depends on `kernel_timespec32_t` exactly matching tracee layout and on the include-time macro set not conflicting with other variants.

Test signals: 32-bit personality tests for `clock_*`, `ppoll_time32`, timer, and `utimensat_time32` style syscalls should show 32-bit seconds/nanoseconds and `UTIME_NOW/OMIT` rendering.
