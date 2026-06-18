# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/usb/hcd/xhci/xhci.h

Main xHCI driver-private header. It defines DMA policy, transfer and ring structures, device/context structures, event and command rings, endpoint/device/pipe state, USBA integration state, attach sequencing, controller state, polled I/O state, quirks, capabilities, and internal function prototypes.

The design is ring-centric: command, event, and transfer rings use `xhci_ring_t`; `xhci_transfer_t` maps USB requests to TRBs and DMA buffers; `xhci_endpoint_t` owns scheduling state and a transfer ring; `xhci_device_t` owns input/output contexts and endpoint pointers.

`xhci_t` aggregates DDI/PCI/MMIO state, register offsets, capabilities, quirks, interrupt handle, DCBAA, scratchpad buffers, command/event rings, taskq entry, controller lock/cv, and USBA root-hub/device/pipe lists.

The file documents important resource limits: 64 KiB TRB transfer chunks, 63 SGL entries for transfer DMA, 512 KiB advertised max transfer, one interrupt by default, interrupt moderation, periodic transfer buffering, endpoint serialization states, and polled-mode persistent error handling.
