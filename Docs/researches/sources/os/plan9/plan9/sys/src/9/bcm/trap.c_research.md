# File Research: sources/os/plan9/plan9/sys/src/9/bcm/trap.c

BCM/ARM trap, interrupt, fault, and debug dump handling.

Key behavior:
- Defines BCM interrupt controller register layout at `VIRTIO+0xB200`.
- `trapinit()` disables interrupts, copies exception vectors/table to high vectors, flushes caches, and sets banked stacks for FIQ/IRQ/abort/undefined/system modes.
- `irqenable()` registers IRQ/FIQ handlers and enables GPU or ARM interrupt bits.
- `irq()` scans registered interrupt handlers and identifies clock interrupts.
- `fiq()` dispatches the single FIQ handler.
- `trap()` adjusts ARM exception return PC, handles IRQ, prefetch abort, data abort, and undefined instruction.
- Data/prefetch faults call `faultarm()` for VM faults or panic/post notes for alignment, access, external abort, parity, and permission cases.
- Undefined user instructions are passed to `fpuemu()` before posting a note.
- Supports scheduling on clock interrupts when `delaysched` is set.
- Provides stack/register dump utilities and `callwithureg()` for debugging.

This file is paired with `lexception.s` and the shared VM/fault and note machinery.
