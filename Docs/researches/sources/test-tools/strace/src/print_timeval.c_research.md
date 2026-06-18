# sources/test-tools/strace/src/print_timeval.c

Purpose: MPERS-aware printer for `kernel_old_timeval_t` and related timeval arrays/interval structures, with Alpha-specific 32-bit timeval support.

Important APIs/types/functions: `print_timeval_t`, `print_struct_timeval`, `print_struct_timeval_data_size`, `print_timeval`, `print_timeval_utimes`, `sprint_timeval`, and `print_itimerval`; under `ALPHA`, `print_timeval32_t`, `print_timeval32`, `print_timeval32_utimes`, `print_itimerval32`, and `sprint_timeval32`.

Control flow: top-level pointer printers fetch tracee memory and print address on failure. Utime arrays are printed with `print_local_array` and append `sprinttime_usec` comments. String printers return `NULL`, an address, or decoded fields depending on verbosity and syscall error state.

State and persistence: string printers use static buffers; no persistent decoder state. All decoded structs are stack-local copies.

Dependencies/integration: uses `DEF_MPERS_TYPE`, `MPERS_DEFS`, `kernel_timeval.h`, `xstring.h`, print field macros, and time comment helpers. Integrated by resource/rusage, select, utimes, and interval timer decoders.

Risks: MPERS layout must match traced personality. The static string buffer is overwritten on subsequent calls. Alpha conditional code has separate ABI assumptions and needs coverage where available.

Test signals: `gettimeofday`, `select`, `utimes`, `setitimer/getitimer`, rusage, null/invalid pointer, and abbrev/non-verbose modes.
