# File Research: sources/os/plan9/9front/sys/src/9/omap/usbehciomap.c

OMAP3-specific EHCI USB host-controller attachment.

Key behavior:
- `ehcireset` stops the controller, clears upper 64-bit address segment if needed, resets hardware, chooses frame-list size, and sets interrupt threshold to one interrupt per millisecond.
- `shutdown` resets/stops EHCI and clears frame-list base.
- `wrulpi` writes ULPI PHY registers through OMAP implementation-specific EHCI register `insn[5]`.
- `reset` probes/configures the OMAP EHCI controller, allocates `Ctlr`, maps capability/operational registers, sets IRQ/port counts, initializes generic EHCI memory, applies OMAP-specific `insn[4]` and ULPI/UTMI setup, links generic EHCI handlers, and enables USB TLL/OTG/EHCI interrupts.
- `usbehcilink` registers the `ehci` HCI type.

Research notes:
- `reset` is single-shot via a static `beenhere`.
- It honors `*nousbehci` and uses `probeaddr(PHYSEHCI)` to skip absent hardware.
