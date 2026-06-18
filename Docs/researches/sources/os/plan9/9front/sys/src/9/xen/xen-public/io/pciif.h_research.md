# File Research: sources/os/plan9/9front/sys/src/9/xen/xen-public/io/pciif.h

Imported Xen public PCI frontend/backend shared structure ABI.

Purpose:
- Defines shared structures and command codes for Xen PCI configuration, MSI/MSI-X, and PCIe AER frontend/backend operations.

Key content:
- Defines `XEN_PCI_MAGIC`.
- Defines shared-info flags for active frontend/backend and AER handler.
- Defines PCI operation codes for config read/write, MSI/MSI-X enable/disable, and AER actions.
- Defines PCI error codes.
- Defines `struct xen_msix_entry`, `struct xen_pci_op`, `struct xen_pcie_aer_op`, and `struct xen_pci_sharedinfo`.

Integration:
- Not used by visible 9front Xen runtime code.
- Vendored control/device protocol context for PCI passthrough.

Risks/notes:
- Large MSI-X entry array must fit expected shared page constraints.
- PCI passthrough operations are privilege/security sensitive.
