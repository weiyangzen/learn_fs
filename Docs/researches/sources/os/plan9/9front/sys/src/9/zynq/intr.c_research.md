# File Research: sources/os/plan9/9front/sys/src/9/zynq/intr.c

Purpose: Zynq interrupt controller driver for the ARM GIC.

Key behavior:
- `intrinit` enables distributor/CPU interface and disables/clears all interrupts on CPU0.
- `intrenable` validates IRQ/type, assigns target CPU for shared interrupts, configures level/edge trigger, priority, handler, and enables the interrupt.
- `intr` reads interrupt acknowledge, dispatches registered handler, writes EOI, and returns whether it was the timer IRQ.

Integration notes: Uses `mpcore` MMIO mapping, `Ureg`, Plan 9 interrupt accounting, and constants from `io.h`.

Risk/attention points: Only one handler function is allowed per IRQ unless it is the same function. IRQ target programming currently selects CPU0 for non-private interrupts.
