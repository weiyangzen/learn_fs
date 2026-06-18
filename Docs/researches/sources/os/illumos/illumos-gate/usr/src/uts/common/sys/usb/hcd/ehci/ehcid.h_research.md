# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/usb/hcd/ehci/ehcid.h

EHCI driver-private header for USB 2.0 host-controller state. It defines `ehci_state_t`, per-pipe private state, transfer wrappers for QTD and ITD-based transfers, bandwidth accounting, kstats, controller lifecycle states, DMA pool sizing, register access macros, and public driver-internal prototypes.

Key responsibilities are asynchronous/periodic schedule tracking, descriptor-pool ownership, root-hub integration, polled console I/O state, frame-number overflow tracking, transfer timeout lists, and HCDI entry points for control, bulk, interrupt, and isochronous transfers.

Concurrency is centered on `ehci_int_mutex`, with Warlock annotations documenting lock protection and stable unlocked fields. The file is a central contract between EHCI attach/init, transfer scheduling, interrupt handling, root-hub emulation, and polled-mode console support.

Important implementation constraints include fixed QH/QTD/ITD pool sizes, DMA sync macros, 20 KiB QTD transaction limit, split-transaction bandwidth constants, and vendor-specific PCI workarounds for NVIDIA, ALI/ULi, NEC combo, and VIA controllers.
