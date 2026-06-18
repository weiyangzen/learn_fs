# File Research: sources/os/plan9/plan9/sys/src/9/kw/usbehci.h

## Role

EHCI host-controller private header for the Kirkwood USB driver. It defines controller state, polling synchronization, operational register layout, debug macros, and linkage prototypes used by `usbehcikw.c` and generic EHCI code.

This is USB host infrastructure, indirectly storage-relevant for USB mass storage.

## Main Contents

- Debug macro overrides:
  - `dprint`, `ddprint`, `deprint`, `ddeprint`
- Opaque types:
  - `Ctlr`, `Eopio`, `Isoio`, `Poll`, `Qh`, `Qtree`
- `Poll`: lock/rendezvous state for polling.
- `Ctlr`: EHCI controller state, frame list, async queue heads, periodic tree, interrupt counters, and load accounting.
- `Eopio`: EHCI operational registers plus Kirkwood/Freescale-specific extension registers.
- Prototypes:
  - `ehcilinkage`
  - `ehcimeminit`
  - `ehcirun`

## Important Behavior

- Models standard EHCI operational registers and the Kirkwood-specific extra OTG/device-mode/Freescale registers.
- `Ctlr` embeds both synchronization and hardware list state.

## Dependencies And Assumptions

- Depends on `Hci`, `Ecapio`, endpoint debug fields, and USB types from port USB headers.
- Assumes one-port EHCI layout in `portsc[1]`.

## Notable Risks

- Register layout includes undocumented or semi-documented vendor extensions.
- Generic EHCI and Kirkwood-specific code must agree on structure layout.
