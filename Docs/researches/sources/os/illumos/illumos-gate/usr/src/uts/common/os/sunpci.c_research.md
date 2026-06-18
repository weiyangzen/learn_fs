# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/os/sunpci.c

## Purpose

`sunpci.c` implements common PCI configuration-space helpers and suspend/resume preservation logic. It saves and restores PCI/PCIe config registers, selected capability registers, and PCI power-management context, including PME wake behavior. This matters to storage and filesystem-adjacent drivers because block devices often sit behind PCI/PCIe controllers whose configuration must survive suspend, resume, detach, and reattach cycles.

## Main Interfaces

Config access:
`pci_config_setup` maps PCI config space register set 0 with little-endian strict-order access and enables fault-managed access when the device supports it. `pci_config_teardown` unmaps it. `pci_config_get8/16/32/64` and `pci_config_put8/16/32/64` derive the mapped address from the access handle and perform typed DDI reads/writes.

Config save/restore:
`pci_save_config_regs` snapshots config registers into devinfo properties. `pci_restore_config_regs` restores those properties and removes them afterward.

Capability save/restore:
`pci_save_caps`, `cap_walk_and_save`, `pci_fill_buf`, `pci_generic_save`, `pci_msi_save`, `pci_pcix_save`, `pci_pcie_save`, `pci_ht_addrmap_save`, `pci_ht_funcext_save`, `pci_pmcap_check`, and `pci_restore_caps` implement capability walking and replay. `pci_cap_table` describes supported capability IDs and capability-specific sizing functions.

Power management:
`pci_lookup_pmcap` finds the PCI PM capability for ordinary header-zero devices. `pci_post_suspend` saves config state, computes an appropriate low-power suspend level with PME enable when possible, disables I/O/memory/bus mastering, optionally enables ACPI wake on x86, and writes PMCSR last. `pci_pre_resume` disables wake, restores PMCSR/D0 timing, and restores saved config space.

## Important Control Flow

PCIe save path:
If capability walking detects `PCI_CAP_ID_PCI_E`, the code allocates a 4 KiB PCIe config buffer plus a readable-word mask. On SPARC it uses `ddi_peek32`; on x86 it uses cautious config access and treats `0xffffffff` as unreadable. It stores `SAVED_CONFIG_REGS_MASK` and `SAVED_CONFIG_REGS` properties.

Conventional PCI save path:
For non-PCIe devices, it saves selected header fields into `pci_config_header_state_t`: command, header type, bridge control for type-one headers, cache line size, latency timers, and BAR0-BAR5. It then saves supported PCI capabilities into a trailing register buffer and stores descriptors in `SAVED_CONFIG_REGS_CAPINFO`.

Capability sizing:
MSI save length depends on 64-bit-address and per-vector-mask support. PCI-X save length depends on version. HyperTransport address-map and function-extension capabilities compute variable lengths from capability registers. PCIe capability save returns zero because PCIe devices are handled by the 4 KiB full-config save path.

Restore path:
PCIe restore replays only masked readable 32-bit words. Conventional restore writes saved command/header-related values, BARs, and saved capability registers. PM capability restore preserves current power-state bits through `pci_pmcap_check` so restoring config space does not accidentally force an unwanted D-state. A final read flushes writes before saved properties are removed.

Suspend path:
`pci_post_suspend` first saves config regs, then caches PM context in `SAVED_PM_CONTEXT`. If no PM capability exists, it records `PPCF_NOPMCAP`. Otherwise it chooses the lowest PME-capable state, preferring D3 hot/cold, then D2, D1, D0, falling back to D3 hot. It clears command-register I/O, memory, and bus master enables before writing PMCSR last.

Resume path:
`pci_pre_resume` reads saved PM context, disables platform wake on x86 if it was enabled, restores PMCSR, delays 10 ms for D3-to-D0 timing, and calls `pci_restore_config_regs`.

## Data and Properties

Persisted device properties:
`SAVED_CONFIG_REGS`, `SAVED_CONFIG_REGS_MASK`, `SAVED_CONFIG_REGS_CAPINFO`, and local `SAVED_PM_CONTEXT` hold suspend/detach context across the relevant framework transitions.

Global control:
`pci_enable_wakeup` gates PME/platform wake handling.

## Research Notes

This file is the common PCI state-preservation layer for illumos. The key storage-relevant behavior is that PCIe devices get full 4 KiB cautious snapshots, while conventional PCI devices get header plus selected capability replay. Power-management code carefully writes PMCSR last on suspend and restores PMCSR before config registers on resume, which is important for devices that stop responding correctly after entering D3.
