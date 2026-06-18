<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/print_time.c -->
# sources/test-tools/strace/src/print_time.c

Purpose: decodes the legacy `time` syscall and formats returned epoch seconds.

Important APIs/types/functions: `SYS_FUNC(time)`, mpers `kernel_time_t`, `sprinttime`, and `tcp->auxstr`.

Control flow: on exit, prints `tloc` and dereferenced time value if accessible. On successful return, sets aux string to human-readable return time.

State and persistence behavior: no persistent state; uses exit-phase syscall result and optional output pointer.

Dependencies and integration points: syscall table integration, mpers scalar sizing, tracee memory fetch, and time formatting helpers.

Risks: pointer output is only valid on exit. Time width is personality-sensitive.

Test signals: `time(NULL)`, valid `tloc`, invalid pointer, syscall failure, 32-bit/64-bit personalities, and aux return string formatting.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/print_time.c -->
