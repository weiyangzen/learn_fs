# File Research: sources/os/plan9/9front/sys/src/9/pc/usbuhci.c

## Role

Plan 9/9front USB Universal Host Controller Interface driver. It binds legacy PCI UHCI controllers into the generic USB HCI layer and implements USB endpoint I/O over UHCI frame lists, queue heads, and transfer descriptors.

## Main Interfaces

- Registers HCI type `uhci` through `usbuhcilink()` and `addhcitype("uhci", reset)`.
- Fills generic `Hci` callbacks: `init`, `interrupt`, `epopen`, `epstop`, `epclose`, `epread`, `epwrite`, `seprintep`, `portenable`, `portreset`, `portstatus`, `shutdown`, and `debug`.
- PCI discovery matches USB serial-class UHCI devices with programming interface `0`, reserves BAR4 I/O ports, and records IRQ/TBDF/port base.

## Key Behavior

- Defines UHCI I/O registers, port-status bits, TD/QH link/status/token bits, and software queue states.
- Owns aligned pools for `Td` and `Qh`; TDs include a small embedded buffer for tiny transfers and optional allocated buffers for larger transfers.
- Builds a 1024-entry UHCI frame list and dummy queue-head chain for control, interrupt, and bulk schedules. A terminal dummy TD loops to itself as a documented PIIX4 erratum workaround.
- Endpoint open allocates per-direction queue state for control, bulk, interrupt, or isochronous endpoints. Endpoint close/cancel aborts queued TDs and waits for hardware state to settle.
- Normal endpoint I/O builds TD chains, links them to a QH, kicks the controller, waits for interrupt/poll completion, updates data toggles, and maps UHCI status bits to errors.
- Control transfers are assembled as setup, optional data, and status phases. Bulk and interrupt transfers are chunked by maximum TD length and endpoint max packet size.
- Isochronous paths support both read and write, maintain per-frame TD pointers, buffer delay, frame-number tracking, and consecutive error accounting.
- Interrupt handling acknowledges controller status, walks active QHs and isochronous streams, transitions completed work to done state, and wakes sleepers. Missed work is handled by wait/poll paths.
- Reset disables legacy mode, stops the controller, issues global and host-controller resets, restores SOF timing, programs frame-list base, enables interrupts, and starts execution.

## Dependencies And Assumptions

- Depends on Plan 9 PCI, I/O-port allocation, interrupt, DMA-visible memory, and generic USB host-controller infrastructure.
- Uses 32-bit PCI window macros for hardware links and assumes DMA-visible frame/QH/TD allocations.
- Supports `*nousbuhci` config opt-out and optional controller selection by I/O port.
- File-level BUG comments note excessive delays/ilocks, incomplete per-frame bandwidth admission, and a simpler interrupt-endpoint schedule than OHCI/EHCI.

## Research Notes

- This is the companion legacy USB transport to `usbohci.c`, important for devices exposed higher in Plan 9 as files.
- Root-hub handling is two-port by default but `init()` probes additional UHCI ports by reading port-status registers.
- UHCI is I/O-port based, unlike OHCI’s MMIO register block.
