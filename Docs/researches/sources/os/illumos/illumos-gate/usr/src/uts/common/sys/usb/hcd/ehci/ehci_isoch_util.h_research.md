# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/usb/hcd/ehci/ehci_isoch_util.h

EHCI isochronous utility prototypes. It declares allocation of isochronous pools, ITW resources, iTD allocation/deallocation/list insertion/removal, iTD count calculation, periodic-frame-list insertion/removal, active-list helpers, done-list creation, isochronous IN resource management, CPU/IOMMU address conversion, error parsing, and iTD/siTD debug printing.

This header separates lower-level resource/list/address helpers from the higher-level isochronous API in `ehci_isoch.h`.
