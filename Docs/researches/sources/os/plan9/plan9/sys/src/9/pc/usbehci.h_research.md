# File Research: sources/os/plan9/plan9/sys/src/9/pc/usbehci.h

Purpose: PC-specific/shared header for the EHCI USB 2.0 host-controller driver. It overrides debug macros, forward-declares EHCI-private structures, defines the controller and operational register structures used by PC EHCI code, and declares linkage functions.

Main structures:
- `Poll`: lock/rendezvous pair with `must`/`does` counters for polling coordination.
- `Ctlr`: EHCI controller runtime state, including PCI device, capability/operational registers, periodic frame list, async QH list, interrupt tree, iso list, load counters, interrupt counters, request count, and poll state.
- `Eopio`: EHCI operational register layout, including command, status, interrupt enable, frame index, segment, frame-list base, async link, config, and port status/control array.

Key declarations:
- Debug macros depend on `ehcidebug` and per-endpoint debug.
- Externs: `ehcidebug`, `ehcidebugcapio`, `ehcidebugport`.
- Functions supplied elsewhere: `ehcilinkage`, `ehcimeminit`, `ehcirun`.

Dependencies and integration:
- Used by `usbehcipc.c` and the generic EHCI implementation under `../port`.
- Depends on EHCI capability register definitions from `portusbehci.h` and USB/HCI structures.

Risks and notes:
- `Eopio` uses a one-element flexible-style `portsc[1]`; code must rely on actual mapped register space for all ports.
- `Ctlr` mixes interrupt, async, periodic, and isochronous state and must be used under the documented locks.
