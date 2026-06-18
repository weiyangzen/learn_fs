# File Research: sources/os/linux/linux-stable/fs/proc/interrupts.c

Creates `/proc/interrupts`.

Key points:
- Defines a simple seq_file iterator over positions `0..irq_get_nr_irqs()`.
- Delegates formatting to architecture/core IRQ function `show_interrupts`.
- Registers `interrupts` during `fs_initcall`.

Dependencies/contracts:
- Depends on generic IRQ numbering and `show_interrupts()`.
- Read-only proc seq entry.
