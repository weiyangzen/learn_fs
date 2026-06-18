# File Research: sources/virtualization/spdk/app/spdk_lspci/spdk_lspci.c

## Purpose
Lists SPDK-visible PCI devices supported by the NVMe driver, including devices behind VMD.

## Main Entry Points
- `usage()` prints help.
- `pci_enum_cb()` is a no-op enumeration callback used to populate SPDK's PCI list.
- `print_pci_dev()` formats PCI address, vendor/device IDs, and VMD annotations.
- `main()` parses `-h`, initializes SPDK env, initializes VMD, enumerates NVMe PCI devices, prints the device list, and finalizes.

## Internal Mechanics
The program initializes SPDK env with app name `spdk_lspci`, calls `spdk_vmd_init()`, enumerates the NVMe PCI driver, and then walks all SPDK PCI devices with `spdk_pci_for_each_device()`.

## Dependencies
Uses SPDK env, PCI, NVMe PCI driver access, and VMD APIs.

## Filesystem/Block Relevance
This utility helps identify NVMe hardware available to SPDK storage applications.

## Risks and Notes
- VMD initialization failure is non-fatal but may hide some NVMe devices.
- The enumeration callback intentionally does not claim or configure devices.
