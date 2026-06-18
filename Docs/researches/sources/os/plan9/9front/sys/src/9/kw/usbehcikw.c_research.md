# File Research: sources/os/plan9/9front/sys/src/9/kw/usbehcikw.c

Kirkwood USB EHCI host-controller glue. It discovers a fixed EHCI controller at `soc.ehci`, configures bridge address windows and PHY registers, invokes generic EHCI memory/linkage, and registers the host-controller type.

`ehcireset` resets the controller, clears high address segment, chooses frame-list size, programs USB bridge windows for two 256 MiB DRAM chip-selects, powers/calibrates the PHY, applies Marvell errata and guideline magic values, and leaves the controller stopped for generic setup.

`reset` allocates/claims one controller, sets HCI port/IRQ/nports, assigns uncached DMA allocation hooks, calls `ehcireset`, `ehcimeminit`, and `ehcilinkage`, and enables the USB interrupt.

Notable risks: many PHY and mode settings are magic values from errata/Linux; `findehcis` assumes fixed Sheeva/Kirkwood addresses and only one controller instance.
