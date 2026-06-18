# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/sata/adapters/ahci/ahcireg.h

## Role

`ahcireg.h` defines AHCI hardware register constants, capability/control/interrupt bits, register address macros, SATA FIS layouts, received-FIS memory layout, PRDT entries, command tables, and command headers.

## Register and Capability Model

The header defines AHCI limits for ports, command slots, and PRDT entries. It provides HBA capability bits for ports, enclosure management, command coalescing, slot count, power states, FIS switching, port multipliers, AHCI-only mode, speed, command-list override, LEDs, staggered spin-up, NCQ, 64-bit addressing, and extended capabilities such as BIOS/OS handoff and DevSleep.

Global register macros compute addresses for CAP, GHC, interrupt status, ports implemented, version, CCC, enclosure management, CAP2, and BOHC.

Per-port macros compute addresses for command-list/FIS bases, interrupt status/enable, command/status, taskfile, signature, SStatus/SControl/SError/SActive, command issue, SNotification, and FIS-based switching.

## Interrupts and Port Bits

Port interrupt bits cover register/PIO/DMA/set-device/unknown FIS events, descriptor processed, connect changes, mechanical presence, PhyRdy, port multiplier errors, overflow, interface/host bus errors, taskfile errors, and cold presence detection.

Port command/status bits cover start, spin-up, power-on, command-list override, FIS receive enable, active command slot, FIS/command-list running, cold/mechanical presence, port multiplier, hotplug, ATAPI, LED, link power management, and ICC state.

## FIS and DMA Structures

The file defines hardware-format structures for:
- host-to-device register FIS.
- device-to-host register FIS.
- set-device-bits FIS.
- DMA setup FIS.
- PIO setup FIS.
- BIST active FIS.
- unknown FIS.
- command FIS.
- received FIS block.

Numerous macros set/get packed FIS fields.

## Command Structures

`ahci_prdt_item_t` describes one physical region descriptor and exposes interrupt-on-completion and byte-count getters.

`ahci_cmd_table_t` contains command FIS, ATAPI CDB area, reserved space, and PRDT array.

`ahci_cmd_header_t` contains command description fields, PRD byte count, command table base addresses, and helper macros for PRDT length, port multiplier port, reset, prefetch, write, ATAPI, and FIS length.

## Research Notes

This is the AHCI hardware ABI header. Correctness depends on exact bit positions, offsets, packed hardware layouts, and PRDT/command-slot sizing.
