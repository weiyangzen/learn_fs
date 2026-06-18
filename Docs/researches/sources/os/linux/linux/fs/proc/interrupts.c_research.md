# File Research: sources/os/linux/linux/fs/proc/interrupts.c

## Scope

This file registers `/proc/interrupts` and supplies a seq_file iterator over IRQ numbers.

## Public And Internal APIs Covered

- Seq operations: `int_seq_ops`.
- Init entry point: `proc_interrupts_init()`.

## Control Flow And Behavior

- The iterator treats `*pos` as the IRQ number slot.
- `int_seq_start()` returns positions from 0 through `irq_get_nr_irqs()`.
- `int_seq_next()` advances until the IRQ limit.
- `show_interrupts()` is the architecture/core IRQ display function used as `.show`.
- `proc_interrupts_init()` registers `interrupts` with `proc_create_seq()` at `fs_initcall` time.

## Dependencies And Risks

- Depends on generic IRQ numbering and `show_interrupts()`.
- The file owns only iteration; formatting and per-architecture IRQ details live outside this file.
