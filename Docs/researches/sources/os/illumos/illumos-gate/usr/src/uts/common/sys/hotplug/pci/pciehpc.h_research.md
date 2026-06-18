# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/hotplug/pci/pciehpc.h

## Role

`pciehpc.h` declares interfaces exported by the PCI Express native hotplug controller extension module.

## Key Interfaces and Data

- Kernel includes bring in DDI hotplug, PCIe implementation state, boolean definitions, and shared `pcie_hp.h`.
- Declares native PCIe hotplug lifecycle and interrupt functions: `pciehpc_init()`, `pciehpc_uninit()`, and `pciehpc_intr()`.
- Declares hotplug ops dispatcher `pciehpc_hp_ops()`.
- Declares helpers to get slot state and set slot name.
- Declares 8/16/32-bit hotplug register read/write helpers.
- Declares `pciehpc_led_init()` for slot LED state initialization.
- Declares slot kstat init/fini helpers.
- On x86, declares `pciehpc_update_ops()` to update platform-specific operations.

## Dependencies and Use

This header is kernel-only for actual declarations. It depends on shared `pcie_hp_t` structures from `pcie_hp.h`.

## Research Notes

The file is a narrow module boundary; it does not define state itself, but operates on the common controller and slot structures.
