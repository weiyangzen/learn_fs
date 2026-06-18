# File Research: sources/os/plan9/9front/sys/src/9/ppc/devirq.c

User-visible IRQ control/waiting device for external IRQs and a millisecond timer.

Key responsibilities:
- Exposes `#b/irq1` through `irq7`, `mstimer`, and `fpgareset`.
- Allocates per-open `Irqconfig` state with enable/mode/count/rendezvous/timer fields.
- Supports control commands: `interrupt on|off`, `mode level|edge` or timer period, `reset`, `wait`, and `debug`.
- Chains multiple open waiters on the same hardware IRQ and enables/disables underlying hardware vectors as needed.
- Implements blocking reads/waits that return interrupt counts plus mode/period.
- Implements `fpgareset` write command.

Dependencies:
- Uses MPC8260 interrupt controller registers through `iomem`, generic `intrenable`/`intrdisable`, timers, and `fpgareset()`.

Notable behavior:
- The directory table appears to assign `Qirq1` to several irq entries, which is notable because the names differ while qid paths repeat for irq3-irq7.
