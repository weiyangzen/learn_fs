# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/hotplug/pci/pcihp.h

## Role

`pcihp.h` defines PCI nexus hotplug extension interfaces, minor-number encoding, and CompactPCI hot-swap constants.

## Key Interfaces and Data

- Kernel declarations include `pcihp_init()`, `pcihp_uninit()`, `pcihp_info()`, and `pcihp_get_cb_ops()`.
- Minor-number macros encode instance and PCI device number and decode them back.
- Special minors are `PCIHP_DEVCTL_MINOR` and `PCIHP_DEBUG_MINOR`.
- CompactPCI capability register offsets identify extended capability pointer, capability ID, next pointer, and hot-swap CSR.
- CompactPCI hot-swap capability ID and CSR bits cover insertion, extraction, LED state, and ENUM mask.
- `PCIHP_MAKE_REG_HIGH()` builds the high word for PCI register specification from bus/device/function/register.
- Success/failure aliases map to DDI return values.
- CompactPCI enum handling constants distinguish handle-and-clear versus clear-only.

## Dependencies and Use

The header is used by PCI nexus hotplug code and CompactPCI support. It is separate from newer `pcie_hp.h` common PCIe structures.

## Research Notes

The minor encoding is part of `/dev/cfg` style attachment-point plumbing; the CompactPCI definitions are legacy but still exposed here.
