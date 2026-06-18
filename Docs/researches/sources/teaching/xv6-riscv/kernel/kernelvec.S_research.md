# File Research: sources/teaching/xv6-riscv/kernel/kernelvec.S

Supervisor-mode trap vector assembly for traps that occur while already in the kernel.

Important behavior:
- Allocates 256 bytes on the current kernel stack.
- Saves caller-saved registers used by C code.
- Calls `kerneltrap()` in `trap.c`.
- Restores registers and returns with `sret`.

Filesystem relevance: indirect but important for device interrupts. Virtio disk and UART interrupts enter through trap handling and can wake filesystem or console operations blocked in sleep.
