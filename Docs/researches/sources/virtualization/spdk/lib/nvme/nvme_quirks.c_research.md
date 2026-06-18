# File Research: sources/virtualization/spdk/lib/nvme/nvme_quirks.c

## Purpose

Maps PCI IDs to SPDK NVMe controller quirk flags. This lets PCIe controller construction adapt behavior for known devices, vendors, and virtual controllers.

## Main Responsibilities

- Define `struct nvme_quirk` entries keyed by `spdk_pci_id`.
- Match Intel, Memblaze, Samsung, VirtualBox, Red Hat, CNEX Labs, VMware, Huawei, Microsoft, and Micron IDs to flags such as latency log quirks, striping, read-zero-after-deallocate, initialization delays, minimum queue sizes, no SGL for DSM, maximum PCI access width, OCSSD, security OACS, MDTS metadata handling, not using SGL, and MSI-X vector count behavior.
- Implement wildcard-aware PCI ID matching where fields in the quirk entry may be `SPDK_PCI_ANY_ID` or class-any.
- Return matching flags from `nvme_get_quirks()` and debug-log each enabled quirk.

## Integration Points

Called by PCIe controller construction in `nvme_pcie.c` after reading `spdk_pci_id` from the PCI device. Flags are consumed across controller setup and qpair submission paths, including CMB command copy width and SGL selection.

## Risk Notes

The table returns the first matching entry. Broad wildcard entries must remain ordered after more specific entries for the same vendor/class to avoid masking device-specific behavior.
