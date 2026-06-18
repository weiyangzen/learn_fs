# sources/test-tools/strace/src/printsiginfo.h

Purpose: Declares public siginfo printing entry points for decoders outside the MPERS implementation unit.

Important APIs/types/functions: prototypes for `printsiginfo`, `printsiginfo_at`, and `print_siginfo_array` or their MPERS-selected names.

Control flow: header-only; callers pass a `struct tcb`, tracee address, or array length and implementation handles memory fetching.

State and persistence: none.

Dependencies/integration: included by ptrace and signal syscall decoders. Depends on core strace types and MPERS symbol naming.

Risks: declarations must remain consistent with `printsiginfo.c`; missing MPERS guards can create duplicate or hidden symbols.

Test signals: build with MPERS enabled/disabled and run ptrace signal-info syscall tests.
