# File Research: sources/os/plan9/9front/sys/src/9/zynq/usbehci.h

Provides the local EHCI controller register definitions and controller state for the Zynq USB host driver.

Key contents:
- Overrides USB debug macros to use `ehcidebug` and endpoint debug flags.
- Defines EHCI link tags, command/status/interrupt/port bits, and Zynq-specific no-op handoff/line macros.
- Declares `Eopio`, matching the controller operational register layout starting around offset `0x140`.
- Declares `Poll` and `Ctlr`, the controller object used by the shared EHCI code.
- `Ctlr` stores locks/rendezvous objects, register pointers, DMA allocator callbacks, periodic frame data, async queue heads, interrupt stats, poll state, base address, IRQ, and mapped register base.
- Declares shared EHCI entry points `ehcilinkage`, `ehcimeminit`, and `ehcirun`.

Notable details:
- This header adapts the common Plan 9 EHCI implementation to the Zynq register layout rather than implementing the full EHCI scheduler itself.
