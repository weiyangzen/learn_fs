# sources/test-tools/strace/src/print_timespec64.c

Purpose: Builds the 64-bit kernel `timespec` printer family from the shared macro template.

Important APIs/types/functions: defines `TIMESPEC_T` as `kernel_timespec64_t` and emits `print_timespec64`, `print_timespec64_data_size`, `print_timespec64_array_data_size`, `print_timespec64_utime_pair`, and `print_itimerspec64`.

Control flow: all behavior is supplied by `print_timespec.h`: size validation, tracee-memory fetches, array iteration, utime special cases, and nested itimerspec printing.

State and persistence: stateless except transient stack copies of tracee data.

Dependencies/integration: includes `kernel_timespec.h` and `print_timespec.h`; used by time64 syscall decoders and inline data decoders that pass explicit byte sizes.

Risks: the array data-size API must reject truncated arrays by checking `nmemb > size / sizeof(TIMESPEC_T)`. Any mismatch in kernel typedef layout would produce wrong field boundaries.

Test signals: time64 syscall tests should cover pointer and inline forms, short buffers, arrays, and failed reads.
