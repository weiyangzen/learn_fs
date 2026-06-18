# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/usb/hcd/openhci/ohcid.h

OHCI driver-private header. It defines missed-interrupt bookkeeping, `ohci_state_t`, per-pipe state, transfer wrappers, controller lifecycle states, descriptor-pool flags, timing constants, bandwidth constants, register/DMA access macros, kstats, debug masks, and internal function prototypes.

The controller state covers DDI/USBA registration, PCI/config/MMIO handles, interrupt allocation, HCCA and ED/TD DMA pools, bandwidth arrays, reclaim lists, root hub, timeouts, frame overflow, SOF/error counters, polled-mode saved register/table state, and kstat handles.

Transfer state is represented by `ohci_pipe_private_t` and `ohci_trans_wrapper_t`, including TD lists, DMA cookies, timeout queue linkage, isochronous packet descriptors, and callback dispatch.

The file documents the operational/error/suspend state model and explicitly records lock ordering between OHCI, USBA pipe, device, and pipe-handle locks. It is the main internal integration point for OHCI scheduling, interrupt completion, root-hub requests, and polled console support.
