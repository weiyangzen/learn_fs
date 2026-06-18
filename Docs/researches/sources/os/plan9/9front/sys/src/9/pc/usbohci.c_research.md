# File Research: sources/os/plan9/9front/sys/src/9/pc/usbohci.c

## Role

Plan 9/9front USB Open Host Controller Interface driver. It binds PCI OHCI controllers into the generic USB HCI layer, owns OHCI endpoint/transfer descriptors, services root-hub port operations, and implements control, bulk, interrupt, and isochronous-output endpoint I/O.

## Main Interfaces

- Registers HCI type `ohci` through `usbohcilink()` and `addhcitype("ohci", reset)`.
- Fills generic `Hci` callbacks: `init`, `interrupt`, `epopen`, `epstop`, `epclose`, `epread`, `epwrite`, `seprintep`, `portenable`, `portreset`, `portpower`, `portstatus`, `shutdown`, and `debug`.
- PCI discovery matches USB serial-class devices with programming interface `0x10`, maps BAR0 MMIO, and records IRQ/TBDF/port base.

## Key Behavior

- Models OHCI hardware structures directly: endpoint descriptors (`Ed`), transfer descriptors (`Td`), host-controller communication area (`Hcca`), MMIO register block (`Ohci`), and a software periodic scheduling tree (`Qtree`).
- Uses pooled aligned ED/TD allocation, physical-address conversion helpers, and a 32-entry HCCA interrupt table for periodic scheduling.
- Maintains control and bulk ED lists through controller head registers, and schedules interrupt/isochronous EDs into a bandwidth-aware tree.
- Builds TD chains for normal endpoint I/O, waits for completion through `Rendez`, records data toggles/errors, clears stalls, and aborts active TDs on cancellation or close.
- Control transfers are assembled as setup, optional data, and status phases; bulk/interrupt transfers chunk requests into bounded TD groups.
- Isochronous support is output-oriented: it preallocates frame TDs, advances frame numbers, buffers samples, and reports underrun/error state. The file comment explicitly lists missing isochronous input streams as a bug.
- `interrupt()` processes writeback-done heads, root-hub status changes, unrecoverable errors, and scheduling overruns, then wakes endpoint waiters.
- Controller reset handles SMM ownership handoff, disables legacy support, initializes HCCA/list registers, enables OHCI lists and interrupts, powers ports, and puts the controller in operational state.

## Dependencies And Assumptions

- Depends on Plan 9 PCI, interrupt, memory-mapping, locking, and generic USB host-controller infrastructure from `../port/usb.h`.
- Uses `xspanalloc` for alignment-sensitive DMA-visible structures and assumes hardware can DMA the addresses produced by `ptr2pa`.
- Supports `*nousbohci` config opt-out and optional controller selection by `hp->port`.
- Uses many controller locks and timed sleeps; comments call out excessive delays/ilocks and incomplete bandwidth admission.

## Research Notes

- This is a core USB storage/input substrate file rather than a filesystem file. It is relevant to subset A because USB mass-storage and other device namespaces depend on this HCI transport.
- Root-hub port status is translated into generic hub status bits (`HPpresent`, `HPenable`, `HPslow`, change flags).
- Error strings map OHCI TD condition codes into user-visible endpoint errors such as CRC, stall, underrun, overrun, and timeout.
