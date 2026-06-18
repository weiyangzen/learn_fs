# File Research: sources/os/plan9/9front/sys/src/9/port/usbehci.c

USB 2.0 EHCI host-controller implementation for the Plan 9 USB stack.

Key responsibilities:
- Defines EHCI hardware register bits, queue states, descriptor flags, and timing/scheduling constants.
- Defines software and hardware descriptor structures for queue heads, queue transfer descriptors, high-speed isochronous TDs, split-transaction isochronous TDs, endpoint I/O state, iso I/O state, descriptor pools, and periodic scheduling trees.
- Allocates aligned EHCI descriptors from a shared pool using controller-provided allocation hooks.
- Starts/stops the controller and initializes async plus periodic schedules.
- Builds and maintains the periodic interrupt scheduling tree with bandwidth accounting.
- Allocates, links, unlinks, and frees queue heads, including async-advance doorbell synchronization.
- Builds TD chains for control, bulk, and interrupt transfers, including embedded buffers for small transfers and DMA buffers for larger transfers.
- Implements transfer wait, timeout, cancellation, polling fallback, and interrupt completion processing.
- Implements control transfers as setup, optional data, and status phases.
- Implements bulk, interrupt, and isochronous endpoint read/write paths.
- Implements high-speed and full-speed isochronous scheduling, descriptor setup, interrupt processing, buffering, delay limiting, and cancellation.
- Handles root-hub port power, reset, enable, and status operations.
- Hands low-speed and full-speed devices off to companion controllers when EHCI should not own them.
- Exposes debug formatting for endpoints and internal dump helpers for queue/TD/iso state.
- Wires EHCI callbacks into `Hci` through `ehcilinkage()`.

Dependencies:
- Uses `usb.h`, `usbehci.h`, Plan 9 locks/rendezvous, DMA flushes, kernel memory allocators, interrupt hooks, and HCI root-port callbacks.
- Depends on controller-specific `Ctlr` fields and register definitions supplied by `usbehci.h`.

Notable behavior:
- The file comments list known limitations: many delays/ilocks, incomplete bandwidth admission control, polling required on some controllers, and missing power-overrun warnings.
- `ehcipoll()` exists because some controllers fail to post completion interrupts reliably.
- `epio()` may detect that polling is required after manually discovering a completed queue in the wait path.
- Isochronous schedules use a virtual 64-frame window replicated across the hardware frame list.
- `epstop()` preserves data toggles for bulk/interrupt endpoints so reopening can resume correctly.
- `ehcimeminit()` initializes frame lists, the async list, the periodic tree, and descriptor preallocation.
