# File Research: sources/os/plan9/9front/sys/src/9/lx2k/usbxhcilx2k.c

LX2K xHCI/DWC3 host-controller glue. It allocates up to two xHCI controllers at fixed MMIO bases, links them to the generic xHCI HCI layer, sets the IRQ, and applies DWC3 core initialization.

`coreinit` programs GCTL, GUCTL, and GFLADJ fields for host mode, power-down scaling, auto-retry, and 30 MHz frame-length adjustment. `reset` allocates the first unused controller and returns it as an `"xhci"` HCI type.

Notable risks: controller discovery is fixed-address and append-only; no shutdown or platform power sequencing appears here.
