# File Research: sources/teaching/xv6-public/proc.h

Defines CPU, context, and process structures.

Contents:
- `struct cpu`: APIC ID, scheduler context, TSS, GDT, started flag, interrupt-disable nesting, interrupt-enabled state, and current process.
- `struct context`: callee-saved registers matching `swtch.S`.
- `enum procstate`: `UNUSED`, `EMBRYO`, `SLEEPING`, `RUNNABLE`, `RUNNING`, `ZOMBIE`.
- `struct proc`: memory size/page table, kernel stack, state, PID/parent, trapframe/context, sleep channel, killed flag, open files, cwd, and debug name.

Role:
- Core scheduler/process ABI shared by process, trap, VM, and assembly code.
