# sources/test-tools/strace/src/linux/bfin/arch_regs.c

Purpose: defines the register storage and program-counter/stack-pointer access macros for the `bfin` Linux strace backend.

Important APIs/types/functions: visible register contract includes macros ARCH_PC_PEEK_ADDR, ARCH_SP_PEEK_ADDR; functions none; notable register fields include architecture struct fields referenced through macros.

Control flow: generic register-fetch code populates the declared storage via `GETREGS`/`GETREGSET`, then syscall-entry/exit, signal, and stack helpers read the macros exported here.

State/persistence behavior: per-tracee register snapshots are held in static architecture globals for the duration of a decode step and refreshed from ptrace; nothing is persisted beyond the trace event.

Dependencies/integration: integrates with generic `get_regs`, `set_regs`, `get_stack_pointer`, syscall-argument extraction, and signal-frame helpers; includes architecture kernel register structs supplied by surrounding includes.

Risks/test signals: wrong register field mapping corrupts syscall numbers, arguments, PC/SP reporting, and injected return values; validate with ptrace register fetch/set tests and known syscall traces on the architecture.

Source-read signal: reviewed complete local file (10 lines).
