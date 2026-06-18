# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/nxge/nxge_virtual.h

## Purpose

`nxge_virtual.h` defines virtualization/shared-resource control operations and state bits for the Neptune/NXGE driver. It is used when multiple functions or domains coordinate access to shared NIU registers, locks, interrupt masks, and common configuration.

## Main Definitions

`nxge_ctl_enum_t` enumerates control operations: query NIU type, get attributes, get/set hardware properties, get/set/update shared registers, acquire blocking or try locks, free locks, set shared registers under lock, clear shared register bits, and clear bits without lock.

Common shared-state bits describe valid/busy state, initialization start/done, TCAM busy, VLAN busy, and NIU PCI reset. `NXGE_SR_FUNC_BUSY_SHIFT` and `NXGE_SR_FUNC_BUSY_MASK` define a shared-register function-busy field.

Configuration category bits identify common TXDMA, RXDMA, RXDMA group, classifier, and quick configuration operations.

## Interfaces

The header exports `nxge_intr_mask_mgmt()` for interrupt-mask management and `nxge_virint_regs_dump()` for virtual interrupt register diagnostics.

## Research Notes

This file has no structs beyond the enum and no implementation. Its correctness depends on consistent shared-register locking across the driver and firmware/hypervisor environment. Race-sensitive areas are busy-bit ownership, clear-without-lock operations, and initialization completion signaling.
