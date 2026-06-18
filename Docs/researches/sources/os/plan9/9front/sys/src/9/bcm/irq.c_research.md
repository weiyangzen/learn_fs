# File Research: sources/os/plan9/9front/sys/src/9/bcm/irq.c

BCM2835-style interrupt controller support for 32-bit ARM kernels.

Key responsibilities:
- Maps interrupt registers at `VIRTIO+0xB200`.
- Tracks handlers as `Vctl` lists indexed by IRQ number.
- Disables CPU and controller interrupts during shutdown.
- Dispatches normal IRQs from pending basic/GPU registers.
- Dispatches FIQ through a separate handler slot.
- Enables IRQs by installing handlers and setting controller enable bits.

Important behavior:
- Returns whether an IRQ was a clock interrupt so trap handling can reschedule.
- Supports shared IRQ handler chains.
- `intrdisable()` is effectively a stub for this platform.

Dependencies:
- Trap entry code, `Ureg`, Plan 9 interrupt registration API, and BCM IRQ constants.
