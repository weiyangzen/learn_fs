# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/hotplug/pci/pcishpc.h

## Role

`pcishpc.h` declares the standard PCI SHPC hotplug controller module interface.

## Key Interfaces and Data

- Declares `pcishpc_init()`, `pcishpc_uninit()`, and `pcishpc_intr()`.
- Declares interrupt enable/disable helpers operating on `pcie_hp_ctrl_t`.
- Declares `pcishpc_hp_ops()` as the DDI hotplug operations dispatcher.

## Dependencies and Use

The header relies on `pcie_hp_ctrl_t` and DDI hotplug types being visible to the including source. It is a module boundary for SHPC backend code.

## Research Notes

This is the SHPC counterpart to `pciehpc.h`, but smaller and without register helper declarations.
