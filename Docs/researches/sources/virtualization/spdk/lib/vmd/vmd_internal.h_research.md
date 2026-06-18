# File Research: sources/virtualization/spdk/lib/vmd/vmd_internal.h

## Purpose

Internal VMD runtime declarations shared by `vmd.c`. It defines the in-memory representation of VMD adapters, VMD-visible PCI buses/devices, BAR mappings, and hotplug memory bookkeeping.

## Key Contents

- Includes SPDK public VMD/env/util/log headers and `vmd_spec.h`.
- Forward declarations for VMD hotplug, adapter, and PCI device objects.
- `struct pci_bars`: virtual address, physical/start address, and size for a BAR.
- `struct vmd_pci_bus`: bus topology node with parent/self pointers, bus number fields, hotplug flags, and device list.
- `struct pci_mem_mgr`: memory-region descriptor used by hotplug BAR allocation queues.
- `struct vmd_hot_plug`: fixed hotplug window state, slot status cache, reserved bus numbers, and free/allocated/unused memory-region queues.
- `struct vmd_pci_device`: embeds `struct spdk_pci_device`, BAR array, parent/subordinate bus links, volatile config/capability pointers, identity/class fields, and hotplug flags.
- `struct vmd_adapter`: one VMD controller, including mapped BARs, VMD bus root, discovered targets, bus list, and scan state.
- Declares `vmd_find_device()`.

## Relationships

- Consumed directly by `vmd.c`.
- Depends on PCI register/capability layouts in `vmd_spec.h`.
- The embedded `spdk_pci_device` lets VMD downstream devices be passed through normal SPDK PCI driver machinery.

## Notes

- Several bitfields pack bus/domain/hotplug state; layout is internal and not serialized.
- Hotplug memory region count is fixed by `ADDR_ELEM_COUNT`.
