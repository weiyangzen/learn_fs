# sources/test-tools/strace/src/print_timex.c

Purpose: Implements printing for kernel `timex`/`ntptimeval` adjustment data and wraps architecture-specific MPERS output.

Important APIs/types/functions: exposes `print_timex` through `MPERS_PRINTER_DECL`; uses helper declarations from `print_timex.h` and xlat tables for clock adjustment modes/status.

Control flow: tracee `timex` data is fetched from an address, printed as a large struct, and abbreviated when global abbrev mode asks for shorter output. Numeric fields such as modes and status are printed with symbolic xlat tables; time fields are printed using timeval/timespec helpers where appropriate.

State and persistence: no persistent state; all contents are read-only copies of tracee memory.

Dependencies/integration: depends on `kernel_timex.h`-style ABI definitions, MPERS, `print_timex.h`, xlat tables for `adjtimex` constants, and syscall decoders for `adjtimex`, `clock_adjtime`, or related calls.

Risks: `struct timex` has architecture and kernel-version layout differences; missing field guards can break portability. Abbreviated mode may hide tail fields, so tests must distinguish intentional truncation from decoding failure.

Test signals: `adjtimex`, `clock_adjtime`, valid/invalid pointers, abbrev/full modes, and personality variants.
