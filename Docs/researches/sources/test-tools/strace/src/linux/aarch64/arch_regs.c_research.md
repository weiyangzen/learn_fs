# sources/test-tools/strace/src/linux/aarch64/arch_regs.c

Purpose: defines the register storage and program-counter/stack-pointer access macros for the `aarch64` Linux strace backend.

Important APIs/types/functions: visible register contract includes macros ARM_cpsr, ARM_pc, ARM_lr, ARM_sp, ARM_ip, ARM_fp, ARM_r10, ARM_r9, ARM_r8, ARM_r7, ARM_r6, ARM_r5; functions none; notable register fields include uregs[18], uregs[16], uregs[15], uregs[14], uregs[13], uregs[12], uregs[11], uregs[10], uregs[9], uregs[8], uregs[7], uregs[6].

Control flow: generic register-fetch code populates the declared storage via `GETREGS`/`GETREGSET`, then syscall-entry/exit, signal, and stack helpers read the macros exported here.

State/persistence behavior: per-tracee register snapshots are held in static architecture globals for the duration of a decode step and refreshed from ptrace; nothing is persisted beyond the trace event.

Dependencies/integration: integrates with generic `get_regs`, `set_regs`, `get_stack_pointer`, syscall-argument extraction, and signal-frame helpers; includes architecture kernel register structs supplied by surrounding includes.

Risks/test signals: wrong register field mapping corrupts syscall numbers, arguments, PC/SP reporting, and injected return values; validate with ptrace register fetch/set tests and known syscall traces on the architecture.

Source-read signal: reviewed complete local file (49 lines).
