# File Research: sources/os/plan9/9front/sys/src/9/xen/xen-public/physdev.h

Purpose: Xen public physical-device operation ABI. It describes `physdev_op` commands for IRQ EOI/status, I/O privilege, APIC access, PIRQ mapping, PCI device registration, MSI/MSI-X coordination, GSI setup, and debug-port reset coordination.

Key interfaces:
- IRQ structs: `physdev_eoi`, `physdev_irq_status_query`, `physdev_irq`.
- Privilege/APIC structs: `physdev_set_iopl`, `physdev_set_iobitmap`, `physdev_apic`.
- PIRQ/PCI structs: `physdev_map_pirq`, `physdev_unmap_pirq`, `physdev_manage_pci*`, `physdev_pci_device_add`, `physdev_pci_device`.
- Compatibility aliases for pre-`0x00030202` names and version-dependent `PHYSDEVOP_pirq_eoi_gmfn`.

Integration notes: Depends on `xen.h`. Intended for privileged guests that own or mediate physical devices.

Risk/attention points: Several operations are version-sensitive or obsolete. Consumers must select the correct EOI-gmfn command based on `__XEN_INTERFACE_VERSION__`.
