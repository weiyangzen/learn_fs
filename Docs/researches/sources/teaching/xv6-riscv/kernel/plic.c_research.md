# File Research: sources/teaching/xv6-riscv/kernel/plic.c

Implements minimal Platform-Level Interrupt Controller setup and interrupt claim/complete operations.

Important behavior:
- `plicinit()` enables nonzero priority for UART and virtio disk IRQs.
- `plicinithart()` enables those IRQs for each hart’s supervisor context and sets priority threshold to zero.
- `plic_claim()` reads the pending interrupt ID.
- `plic_complete()` reports completion.

Filesystem relevance: virtio disk completion interrupts flow through the PLIC and wake blocked disk I/O in `virtio_disk.c`.
