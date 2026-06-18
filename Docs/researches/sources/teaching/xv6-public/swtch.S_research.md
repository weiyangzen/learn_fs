# File Research: sources/teaching/xv6-public/swtch.S

Low-level context switch routine.

Behavior:
- Implements `void swtch(struct context **old, struct context *new)`.
- Saves callee-saved registers on the current stack.
- Stores the old stack pointer through `old`.
- Loads the new stack pointer from `new`.
- Restores callee-saved registers and returns into the new context.

Important interaction:
- Stack layout matches `struct context` in `proc.h`.
