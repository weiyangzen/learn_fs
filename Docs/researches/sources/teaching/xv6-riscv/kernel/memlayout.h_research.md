# File Research: sources/teaching/xv6-riscv/kernel/memlayout.h

Defines physical and virtual memory layout for QEMU’s RISC-V virt machine.

Contents:
- MMIO addresses and IRQ numbers for UART, virtio disk, and PLIC.
- Kernel physical base and `PHYSTOP`.
- `TRAMPOLINE`, `TRAPFRAME`, and `KSTACK(p)` virtual layout.
- User memory layout comments.

Filesystem relevance: provides device MMIO addresses for UART/virtio disk and constants used by VM/trap code. Virtio disk address and IRQ definitions are essential for block I/O.
