# File Research: sources/teaching/xv6-riscv/kernel/proc.h

Defines process, CPU, context switch, and trapframe structures.

Contents:
- `struct context` stores callee-saved registers for `swtch`.
- `struct cpu` tracks current process, scheduler context, interrupt nesting, and prior interrupt state.
- `struct trapframe` is the per-process register save area used by trampoline code.
- `enum procstate` defines lifecycle states.
- `struct proc` stores lock-protected scheduling/lifecycle state plus private process state such as kernel stack, memory size, page table, trapframe, open files, cwd, and name.

Filesystem relevance: `ofile[]` and `cwd` connect processes to the file and inode layers. `trapframe` holds syscall arguments and return values.
