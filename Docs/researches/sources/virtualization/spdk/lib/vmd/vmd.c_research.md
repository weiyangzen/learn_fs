# File Research: sources/virtualization/spdk/lib/vmd/vmd.c

## Purpose

Implements SPDK's Intel VMD PCI device provider. It discovers VMD controllers, maps their config/memory BARs, enumerates PCIe topology behind each VMD, exposes downstream NVMe endpoints as SPDK PCI devices of type `"vmd"`, and handles VMD hotplug/hotremove/rescan paths.

## Main Responsibilities

- Maintains global `g_vmd_container`, with up to `MAX_VMD_SUPPORTED` adapters.
- Maps VMD BAR0 as config space and BAR2 as memory window.
- Walks PCI buses behind VMD using config-space MMIO and constructs `vmd_pci_bus` / `vmd_pci_device` trees.
- Assigns BAR windows for endpoints and bridges, including a small per-hotplug-port memory allocator.
- Detects PCI/PCIe capabilities: PCIe, MSI, MSI-X, serial number.
- Hooks VMD-backed NVMe endpoints into the SPDK NVMe PCI driver via `spdk_pci_hook_device`.
- Registers a PCI provider named `vmd` with attach/detach callbacks.
- Provides public VMD operations:
  - `spdk_vmd_init`
  - `spdk_vmd_fini`
  - `spdk_vmd_pci_device_list`
  - `spdk_vmd_hotplug_monitor`
  - `spdk_vmd_remove_device`
  - `spdk_vmd_rescan`
  - `vmd_find_device`

## Key Control Flow

- `spdk_vmd_init()` calls `spdk_pci_enumerate(spdk_pci_vmd_get_driver(), vmd_enum_cb, ...)`.
- `vmd_enum_cb()` enables memory/bus mastering, initializes `vmd_adapter`, maps VMD BARs, increments adapter count, then calls `vmd_enumerate_devices()`.
- `vmd_enumerate_devices()` selects the VMD internal bus range, including ICX bus restriction handling, then calls `vmd_scan_pcibus()`.
- `vmd_scan_pcibus()` clears stale root-port config, scans depth-first with `vmd_scan_single_bus()`, logs topology, and caches scan-complete signatures in root-port prefetch upper registers.
- `vmd_scan_single_bus()` allocates device objects, distinguishes bridges from endpoints, allocates downstream bus numbers, initializes hotplug windows, recursively scans bridges, and initializes endpoints with `vmd_init_end_device()`.
- `vmd_init_end_device()` assigns BARs, sets up MSI-X masking/enabling, initializes the embedded `spdk_pci_device`, and hooks supported NVMe devices.

## Data Structures

Defined mostly in `vmd_internal.h`, used here as mutable runtime state:

- `vmd_container`: fixed global array of VMD adapters.
- `vmd_adapter`: per-controller BAR mappings, bus list, target NVMe list, address window state.
- `vmd_pci_bus`: topology node with bus numbers and device list.
- `vmd_pci_device`: SPDK PCI wrapper plus raw config-space header/capability pointers and BAR metadata.
- `vmd_hot_plug`: per-hotplug bridge memory allocator and reserved bus state.
- `pci_mem_mgr`: free/allocated/unused region descriptors for hotplug BAR allocation.

## Dependencies

- SPDK PCI/env APIs: `spdk_pci_enumerate`, `spdk_pci_device_map_bar`, `spdk_pci_hook_device`, `spdk_pci_unhook_device`, `spdk_pci_device_detach`.
- SPDK NVMe PCI driver lookup: `spdk_pci_nvme_get_driver`.
- PCI constants and packed register layouts from `vmd_spec.h`.
- Internal runtime structs from `vmd_internal.h`.

## Notable Behaviors

- Only storage express class devices (`PCI_CLASS_STORAGE_EXPRESS`) are treated as supported endpoints.
- VMD-backed PCI devices always use function 0 in attach path.
- Reuses root-port prefetch upper registers as scan-complete signatures.
- For IOMMU/IOVA correctness, VMD BAR physical addresses are read from config space rather than trusting `spdk_pci_device_map_bar()` physical output.
- Hotplug monitor checks PCIe slot/link status, scans for new devices after link-up, and marks missing devices pending removal on link-down.
- Multifunction devices are assumed absent behind VMD.

## Risks / Caveats

- Much of the code manipulates volatile PCI config-space register structs directly; correctness depends on struct layout matching hardware.
- Hotplug memory allocation has a fixed descriptor count (`ADDR_ELEM_COUNT`) and fixed reserved hotplug buses (`RESERVED_HOTPLUG_BUSES`).
- Only 32-bit bridge memory base/limit paths are handled in comments around base/limit propagation.
- Several error paths return generic `-1` or `-ENODEV`, so diagnostics depend heavily on SPDK logs.
