# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/os/pcifm.c

## Purpose

`pcifm.c` implements PCI and PCI-X fault-management support for non-PCIe systems. It gathers PCI error registers, posts ereports, dispatches error callbacks, clears error status, and asynchronously maps target physical addresses back to affected device nodes.

Read completely: 1,506 lines.

## Main Responsibilities

- Defines PCI, PCI bridge, PCI-X, and PCI-X secondary error-class tables.
- Sets up and tears down per-device `pci_erpt_t` state in the device fault-management handle.
- Reads standard PCI status/command, bridge status/control, PCI-X status, and PCI-X ECC registers.
- Converts register bits into fault-management ereports with severity tracking.
- Handles expected, unexpected, and poke error paths.
- Dispatches child fault handlers below PCI bridges.
- Queues target-device ereports from captured physical addresses.
- Provides panic-safe device tree walking and ereport posting.

## Register Gathering and Clearing

`pci_config_check()` checks access-handle fault state after config-space reads, optionally posts a nonrecoverable ereport, and clears access errors.

`pci_regs_gather()` reads generic PCI status and command registers, and for bridges reads secondary status and bridge control. If the device has PCI-X capability, it delegates to `pcix_regs_gather()`.

`pcix_regs_gather()` handles leaf versus bridge PCI-X layouts. PCI-X bridge ECC state may have two ECC register banks; leaf devices have one. `pcix_ecc_regs_gather()` reads ECC status, first address, second address, and attributes.

`pci_regs_clear()` and `pcix_regs_clear()` write saved status values back to clear error bits and reset validity flags.

## Setup and Teardown

`pci_ereport_setup()` validates that the device supports ereports or error callbacks, allocates `pci_erpt_t`, sets up PCI config access, detects bridge headers, records BDF from the `reg` property, detects PCI-X capability, gathers and clears any preexisting errors, then stores the result in `devi_fmhdl->fh_bus_specific`.

`pcix_ereport_setup()` allocates PCI-X leaf or bridge register structures and optional ECC register storage based on PCI-X version.

`pci_ereport_teardown()` frees PCI-X structures, tears down config access, frees bridge register state, and clears `fh_bus_specific`.

## Error Classification

`pci_error_report()` posts generic PCI errors for unexpected faults, delegates PCI-X handling, delegates bridge handling, and uses bus-specific address or BDF data to locate affected access or DMA handles.

`pci_bdg_error_report()` posts bridge secondary-status errors, handles discard timer status, treats cautious get/put and poke cases specially, and dispatches errors to children through `ndi_fm_handler_dispatch()`.

`pcix_error_report()` and `pcix_bdg_error_report()` post PCI-X status and secondary-status ereports.

`pcix_ecc_error_report()` classifies ECC phase and correctability, posts ECC address/attribute/data and secondary CE/UE ereports, and uses `pcix_check_addr()` to populate fault-management bus-specific address or BDF data.

Severity is tracked with local `fatal`, `nonfatal`, `unknown`, and `ok` counters via `PCI_FM_SEV_INC()`.

## Public Posting Path

`pci_ereport_post()` is the main entry point. It is a no-op on PCIe systems because PCIe fault handling is delegated to the PCIe misc module. Otherwise it normalizes older `ddi_fm_error_t` formats, creates a PCI bus-specific payload when needed, ensures an ENA exists, gathers registers, reports errors, clears registers, and updates the caller's status and ENA.

## Target Error Queue

`pci_targetq_init()` creates `pci_target_queue`, a vital error queue drained by `pci_target_drain()`.

`pci_target_enqueue()` packages ENA, class, bridge type, and physical address into `pci_target_err_t` and dispatches it asynchronously.

`pci_target_drain()` walks from the root to find a top-level PCI/PCIe nexus whose `ranges` property contains the physical address, translates it to PCI address space, then walks children to find a matching `reg` or `assigned-addresses` entry and posts a target-device ereport.

`pci_fm_walk_devs()` is a private panic-safe device-tree walker that avoids normal sleeping and locking. `pci_fm_ereport_post()` uses errorq nvlist storage in panic context and normal nvlist posting otherwise.

## Address Mapping Helpers

`pci_check_ranges()` handles top-level PCI nexus `ranges` translation, including config-space bus-range checks and a SPARC `pci_fix_ranges()` compatibility adjustment for psycho-class host bridges.

`pci_check_regs()` matches translated PCI addresses against child `reg` and `assigned-addresses` properties, recording the target `dev_info_t`.

## Notable Invariants

- PCIe systems are skipped based on bus private data.
- Register validity flags prevent clearing or reporting stale/unreadable state.
- Panic paths avoid sleeping locks and use reserved errorq storage.
- Target address mapping assumes PCI-PCI bridges are transparent.
- PCI-X ECC handling has separate bridge and leaf layouts.

## Research Relevance

This file is relevant to storage and filesystem reliability because PCI fault handling underlies HBA, NVMe, NIC, and storage controller error diagnosis. It also shows how illumos maps bus-level faults back to device-tree nodes and driver-owned handles.
