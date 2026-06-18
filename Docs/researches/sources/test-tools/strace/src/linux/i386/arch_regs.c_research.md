# sources/test-tools/strace/src/linux/i386/arch_regs.c

Purpose: defines the register storage and program-counter/stack-pointer access macros for the `i386` Linux strace backend.

Important APIs/types/functions: visible register contract includes macros ARCH_REGS_FOR_GETREGS, ARCH_PC_REG, ARCH_SP_REG, ARCH_MIGHT_USE_SET_REGS; functions none; notable register fields include eip, esp.

Control flow: generic register-fetch code populates the declared storage via `GETREGS`/`GETREGSET`, then syscall-entry/exit, signal, and stack helpers read the macros exported here.

State/persistence behavior: per-tracee register snapshots are held in static architecture globals for the duration of a decode step and refreshed from ptrace; nothing is persisted beyond the trace event.

Dependencies/integration: integrates with generic `get_regs`, `set_regs`, `get_stack_pointer`, syscall-argument extraction, and signal-frame helpers; includes architecture kernel register structs supplied by surrounding includes.

Risks/test signals: wrong register field mapping corrupts syscall numbers, arguments, PC/SP reporting, and injected return values; validate with ptrace register fetch/set tests and known syscall traces on the architecture.

Source-read signal: reviewed complete local file (15 lines).
