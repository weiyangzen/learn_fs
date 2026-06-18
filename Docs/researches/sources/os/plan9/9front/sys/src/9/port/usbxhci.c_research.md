# File Research: sources/os/plan9/9front/sys/src/9/port/usbxhci.c

Plan 9 USB xHCI host-controller implementation backing the generic `Hci` USB interface.

Key responsibilities:
- Defines xHCI register, port, TRB, command, event, completion, controller, slot, endpoint-ring, and wait-state machinery.
- Initializes the controller: maps capability/operational/runtime/doorbell registers, performs BIOS/OS handoff, resets the controller, allocates scratchpad buffers, device-context base array, command ring, and event ring.
- Starts the controller, enables interrupts, tracks microframe wrap events, and runs an `xhcirecover` kernel process for controller or event-ring failure recovery.
- Queues TRBs on command and endpoint rings, rings doorbells, waits for completion events, maps xHCI completion codes to Plan 9 errors, and aborts or stops endpoints on timeout/error paths.
- Allocates/free xHCI slots, builds input/output device contexts, addresses devices, and configures endpoint contexts for control, bulk, interrupt, and isochronous endpoints.
- Implements endpoint open/stop/close/read/write hooks, including control setup/data/status sequences, normal transfer TRBs, and isochronous frame scheduling/buffering.
- Implements port status, reset, warm reset, power, and disable operations for USB 2 and USB 3 style ports.
- Exposes allocation/linkage helpers `xhcialloc()`, `xhcilinkage()`, `xhciinit()`, and `xhcishutdown()`.

Dependencies:
- Uses the Plan 9 port USB layer (`Hci`, `Udev`, `Ep`, endpoint transfer types), kernel DMA/cache helpers, locks/rendezvous, and PCI-style interrupt hooks.
- Uses architecture-supplied DMA address conversion through `ctlr->dmaaddr`, defaulting to `PADDR()` unless a bus wrapper overrides it.

Notable behavior:
- Command submissions serialize through `cmdlock`; slot changes serialize through `slotlock`.
- Event handling resolves completion events back to pending `Wait` objects by matching TRB DMA addresses.
- Control writes special-case `SET_ADDRESS` requests because xHCI address assignment is handled by the `ADDRESS DEVICE` command.
- Recovery shuts down the HCI, marks command and endpoint rings stopped, wakes all waiters, waits for devices to detach, releases DMA structures, and attempts reinitialization.
