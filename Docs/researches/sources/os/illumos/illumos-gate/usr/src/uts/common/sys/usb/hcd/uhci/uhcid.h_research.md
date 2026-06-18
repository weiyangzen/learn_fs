# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/usb/hcd/uhci/uhcid.h

UHCI driver-private state header. It defines root-hub state, `uhci_state_t`, DMA binding flags, polled-mode flags, per-pipe state, transfer wrapper state, DMA address conversion macros, kstats, controller lifecycle states, and debug masks.

`uhci_state_t` tracks DDI/USBA registration, MMIO/config handles, interrupt state, frame-list DMA, TD/QH pools, open/close serialization, root-hub timer state, command timeout handling, bandwidth arrays, outstanding TD queues, control/bulk queue heads, SOF synchronization, polled frame table state, software frame number, pending bulk commands, logging, kstats, and debug I/O base.

`uhci_trans_wrapper_t` carries DMA buffer metadata, TD chains, callback state, byte counters, timeout counters, isochronous buffers, bulk/isoc TD pools, and claim state to prevent duplicate deallocation.

The file encodes UHCI’s simpler controller state machine: init, suspend, operational, and error. Lock annotations mirror the other HCDs and make `uhci_int_mutex` the main state guard.
