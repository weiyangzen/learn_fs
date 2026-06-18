# File Research: sources/os/plan9/plan9/sys/src/9/kw/usbehcikw.c

## Role

Kirkwood-specific EHCI USB host-controller driver glue. It configures address windows, resets the controller, wires generic EHCI methods into Plan 9's USB `Hci` interface, and registers the controller.

This is USB hardware support, indirectly storage-relevant for USB disks.

## Main Interfaces

- `usbehcilink()`: registers the EHCI controller type.
- HCI operations:
  - `reset`
  - `shutdown`
  - `setdebug`
- Internal setup:
  - `findehcis`
  - `ehcireset`
  - `ctlrreset`
  - `setaddrwin`
  - `addrmapdump`

## Data Structures

- `Kwusbtt`: target translation registers for USB address decode.
- `Kwusb`: Kirkwood USB register block including bridge, address windows, control, error status, and capability/control areas.
- `Usbwin`: decoded address window metadata.

## Important Behavior

- Configures up to four USB address decode windows for DRAM chip-select regions.
- Resets and halts EHCI, clears interrupts, configures all ports to host controller routing, and sets USB mode to host.
- Allocates a `Ctlr`, initializes generic EHCI memory, and runs the controller.
- Uses fixed Kirkwood addresses rather than PCI discovery.

## Dependencies And Assumptions

- Includes generic USB/EHCI headers and `usbehci.h`.
- Uses global `soc.ehci`.
- Assumes Kirkwood-style address windows and one EHCI controller.

## Notable Risks

- Address-window setup must match physical DRAM layout or DMA will fail.
- Fixed-address discovery limits portability to this SoC family.
