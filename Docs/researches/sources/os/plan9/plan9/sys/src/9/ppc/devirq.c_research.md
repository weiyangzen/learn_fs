# File Research: sources/os/plan9/plan9/sys/src/9/ppc/devirq.c

## Role

Exposes board external IRQ lines, a millisecond timer, and FPGA reset through a Plan 9 device.

## Main Data

`irqdir` exposes `irq1` through `irq7`, `mstimer`, and `fpgareset`. `Irqconfig` tracks enable state, level/edge or timer interval mode, interrupt counts, wait rendezvous, a linked-list node, and embedded `Timer`. Global `irqconfig[NIRQ]` maps qids to waiter lists.

## Control Flow

Opening an IRQ file allocates an `Irqconfig`; closing disables it and frees state. Writes parse commands: `interrupt on/off`, `mode level/edge` or timer interval, `reset`, `wait`, and `debug`. Enabling a hardware IRQ links the config and installs `intrenable` on `IRQ0 + irq`; enabling `mstimer` installs a periodic timer. Reads block until the interrupt count changes, then return count and mode/interval. The interrupt handler clears pending external IRQ bits, increments all linked configs, and wakes waiters.

## Dependencies

Uses MPC8260 interrupt registers in `iomem`, Plan 9 timers, `intrenable`/`intrdisable`, `fpgareset`, and command parsing helpers.

## Risks

Several `irqdir` entries for irq3-irq7 have qid `{Qirq1}`, which looks like a copy-paste bug. Hardware register writes are board-specific. Each open gets independent counters, but shared interrupt mode is global hardware state.
