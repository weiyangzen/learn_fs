# File Research: sources/os/plan9/plan9/sys/src/9/ppc/msaturn.c

UCU/Saturn PPC board support for interrupt controller setup, machine initialization, trap vectors, and basic reboot hooks.

Key responsibilities:
- Defines Saturn interrupt-controller register addresses and priority mapping.
- Initializes interrupt priority registers and disables all interrupts.
- Enables/disables interrupts by matching requested Plan 9 vector numbers to priority slots.
- Reads interrupt acknowledge/priority register in `intvec` and acknowledges via `intack`.
- Initializes `Mach`, bus/CPU/cycle frequencies, machine-check enable, L2/cache/HID state, FPU baseline, and default `plan9.ini`.
- Installs normal exception vectors through `sethvec`.
- Provides no-op `sharedseginit` and `reboot`.

Important behavior:
- CPU frequency is inferred from PLL register value; bus frequency from Saturn system config.
- Enables L2-related state through `getl2cr`/`putl2cr` and HID0 bits.
- Default configuration selects `ether0=type=saturn` and `sys=ucu`.

Dependencies:
- Depends on `msaturn.h`, `ucu.h`-selected memory constants, PPC assembly cache/SPR helpers, and generic trap code.

Notable risks:
- Interrupt mapping is tiny and board-specific.
- `intvec` logs and acknowledges unknown interrupt priorities.
- Reboot is unimplemented.
