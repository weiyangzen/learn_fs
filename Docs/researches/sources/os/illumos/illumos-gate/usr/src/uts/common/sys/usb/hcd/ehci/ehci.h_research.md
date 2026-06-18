# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/usb/hcd/ehci/ehci.h

Hardware-facing EHCI host controller header. It defines DMA alignment/attribute limits, EHCI capability and operational register layouts, register bitfields, root-hub port bits, extended capability/BIOS handoff bits, periodic frame list layout, queue heads, queue transfer descriptors, and isochronous transfer descriptors.

Core structures include `ehci_caps_t`, `ehci_regs_t`, `ehci_periodic_frame_list_t`, `ehci_qh_t`, `ehci_qtd_t`, and `ehci_itd_t`. The QH/QTD/iTD definitions include both hardware-visible fields and HCD-private software bookkeeping fields for ownership, active/reclaim lists, transfer wrappers, state, frame numbers, and offsets.

The file is central to EHCI transfer scheduling: it encodes async/periodic scheduler controls, root hub port control, QH endpoint/split controls, QTD status/PID/error fields, iTD high-speed isochronous controls, and siTD full/low-speed split isochronous bitfields.

It is not a standalone state header; it depends on broader EHCI state/pipe/wrapper types declared elsewhere.
