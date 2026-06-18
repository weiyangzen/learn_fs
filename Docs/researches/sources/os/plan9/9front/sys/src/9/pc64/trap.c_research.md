# File Research: sources/os/plan9/9front/sys/src/9/pc64/trap.c

amd64 trap, interrupt, syscall, page-fault, notification, register, and debug exception handling.

Key behavior:
- `trapinit0` initializes the IDT at `IDTADDR`, pointing each vector at the assembly vector table and granting user privilege only to breakpoint and syscall vectors.
- `trapinit` initializes IRQ handling, enables NMI, and registers handlers for debug, breakpoint, page fault, double fault, and reserved vector 15.
- `trap` enters kernel context, protects FPU state, dispatches IRQs or user traps, handles recoverable kernel faults from special MSR/peek instruction wrappers, reports unexpected traps, delivers notes, exits kernel context, and restores FPU state.
- `dumpregs`, `callwithureg`, and stack dump helpers print register and stack diagnostics.
- Debug handlers translate hardware watchpoint/debug exceptions and breakpoints into user notes where possible.
- `faultamd64` resolves page faults through the VM fault path, with special handling for kernel faults while copying user memory.
- `syscall` is entered directly from assembly, runs `dosyscall`, arranges `noteret` when notes must be delivered, handles delayed scheduling, and exits kernel/FPU context.
- `notify` and `noted` build and restore user note frames on the user stack.
- `execregs`, `userpc`, `setregisters`, `kprocchild`, `forkchild`, `setkernur`, and `dbgpc` manage user/kernel register contexts.

Notable dependencies:
- Assembly entry/exit paths in `l.s`.
- VM fault handling, notes, process debug locks, and IRQ dispatch.
- Segment selectors and user-address constants from `mem.h`.

Research notes:
- Fault recovery for `_rdmsrinst`, `_wrmsrinst`, and `_peekinst` is coordinated with labels exported by `l.s`.
- `setregisters` masks user-modified segment registers, flags, and PC canonical bits after copying user register state.
