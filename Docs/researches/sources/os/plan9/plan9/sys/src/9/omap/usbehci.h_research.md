# File Research: sources/os/plan9/plan9/sys/src/9/omap/usbehci.h

OMAP EHCI support header extending generic Plan 9 USB/EHCI definitions.

Key contents:
- Overrides EHCI debug print macros to use `ehcidebug` and endpoint debug flags.
- Forward-declares EHCI controller and queue structures.
- Defines `Poll` synchronization state.
- Defines `Ctlr`, the controller state used by generic EHCI code:
  - register pointers,
  - frame list,
  - async and periodic queue heads,
  - isochronous state,
  - interrupt/load counters,
  - poll rendezvous.
- Defines OMAP-specific `Eopio` operational register layout, including three ports and implementation-specific `insn[]` registers.
- Defines `Uhh` USB host subsystem register layout and `P1ulpi_bypass`.
- Declares EHCI globals and generic helper functions.

Role:
- Bridges the generic `portusbehci` driver and the OMAP-specific EHCI reset/register plumbing.

Notable details:
- `Eopio` includes OMAP implementation-specific registers beyond standard EHCI operational registers.
- Controller struct is shared with generic EHCI routines, so field layout matters across files.
