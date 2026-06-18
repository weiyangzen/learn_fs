# File Research: sources/os/plan9/9front/sys/src/9/cycv/intr.c

Cyclone V interrupt controller support.

Key responsibilities:
- Initializes interrupt controller distributor/CPU interface state.
- Installs interrupt handlers by IRQ number.
- Enables interrupts with level/edge configuration.
- Dispatches pending interrupts to registered handlers.
- Tracks interrupt counts and clock interrupt behavior.

Important behavior:
- Uses GIC-like register layout through MPCore base.
- Maintains handler chains through `Vctl` records.
- `intr()` is the C dispatch target from trap assembly.

Dependencies:
- MPCore interrupt registers, `io.h` IRQ constants, trap assembly, and Plan 9 interrupt API.
