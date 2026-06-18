# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/usb/hcd/openhci/ohci.h

OHCI hardware-facing header. It defines operational registers (`ohci_regs_t`), register bit masks, the Host Controller Communications Area (`ohci_hcca_t`), endpoint descriptors (`ohci_ed_t`), transfer descriptors (`ohci_td_t`), and isochronous DMA-buffer metadata.

The file captures the shared HCD/HC memory layout and register protocol: control/status registers, list-head registers, frame registers, root-hub registers, HCCA interrupt table and done-head handling, ED state, TD condition codes, and control-transfer phase markers.

It also establishes DMA alignment and scatter/gather constraints, including ED/TD/HCCA alignment and architecture-specific DMA attribute maxima. The ULI1575 workaround constants show reset-time hardware cleanup requirements for registers that do not return to defaults.

This is a low-level ABI header between software and OHCI hardware; mistakes here affect DMA layout, MMIO interpretation, done-list parsing, and root-hub port status handling.
