# File Research: sources/os/plan9/plan9/sys/src/9/omap/usbehciomap.c

OMAP3-specific EHCI host-controller reset, setup, shutdown, and linkage code.

Key responsibilities:
- `ehcireset()` stops EHCI, clears 64-bit segment address, resets controller unless it is the debug controller, configures interrupt threshold, and records frame-list size.
- `shutdown()` resets/stops the controller and clears the frame-list base.
- Provides `setdebug()` to update global EHCI debug level.
- Implements OMAP-specific ULPI register writes through `wrulpi()`.
- `reset()` probes for EHCI presence, allocates `Ctlr`, maps capability/operational registers, initializes controller memory, configures OMAP implementation registers and ULPI/UTMI mode, links to generic HCI, and enables extra USB-related interrupts.
- `usbehcilink()` registers this HCI type as `"ehci"`.

Important behavior:
- Skips initialization when `*nousbehci` is set or `probeaddr(PHYSEHCI)` fails.
- Only allows one initialization through static `beenhere`.
- OMAP setup sets `insn[4]` bit 5 as required by the manual.
- For ULPI port 1, disables the integrated STP pull-up and forces PHY high-speed mode.
- Registers extra interrupts for USB TLL and OTG/OTG DMA.

Dependencies:
- Depends on generic USB HCI/EHCI port code, OMAP memory addresses, `probeaddr`, Plan 9 interrupt registration, and `usbehci.h`.

Notable risks:
- ULPI polling loop uses a counterintuitive condition documented as contrary to sparse documentation.
- GPIO PHY reset is noted as TODO.
- `hp->irq` is set to 77 but additional interrupt enables use 78, 92, and 93.
