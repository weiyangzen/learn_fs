# sources/test-tools/strace/src/print_timex.h

Purpose: Declares the timex printer interfaces shared by syscall decoders and MPERS-generated implementations.

Important APIs/types/functions: declares `print_timex`-family entry points and related helper prototypes for printing `timex`-style structures.

Control flow: header only; compile-time integration controls which concrete implementation and personality-specific symbol is visible.

State and persistence: none.

Dependencies/integration: included by `print_timex.c` and syscall decoders using `adjtimex`/`clock_adjtime` output. Depends on `struct tcb` and `kernel_ulong_t` definitions from core strace headers.

Risks: prototype drift between this header and MPERS implementation will break builds across personality configurations.

Test signals: build all configured personalities and run time-adjustment syscall tests.
