# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/sata/impl/sata.h

## Role

Internal SATA framework header. It defines framework-private HBA instance state, controller/device/port runtime state, SCSI-to-SATA packet translation state, event flags, minor-number encoding, target-number encoding, and debug hooks.

## Key Elements

- `sata_hba_inst_t` tracks one registered SATA HBA instance: devinfo, linked-list links, SCSI and SATA transport pointers, taskq, event/open flags, controller stats, and controller port array.
- `sata_cport_info_t` tracks a controller port: address, mutex, state/events, SCR copy, device type, attached drive or port multiplier, link/attach timestamps, stats, and target-node cleanliness.
- `sata_drive_info_t` tracks attached drive identity, state/events, status/error registers, feature support/enabled flags, queue depth, capacity, IDENTIFY data, stats, standby timer, and saved power level.
- `sata_pmult_info_t` and `sata_pmport_info_t` track port multiplier state and child device ports.
- Defines power levels, PM capability mappings, valid device masks, device feature bits, drive setting bits, and internal event/lock flags.
- `sata_pkt_txlate_t` links SCSI packet, SATA packet, DMA handles/cookies, temp buffers, and transfer window state.
- Defines ATA pass-through sense data and additional SCSI ASC constants used by translation.
- Defines `SATA_IS_MEDIUM_ACCESS_CMD()` for identifying commands that access media.
- Provides many accessor macros for transport callbacks, port structures, drive structures, pmult structures, packet translation fields, and task queues.
- Defines devctl/AP minor-number layout and SCSI target encoding for direct and port-multiplier-attached devices.
- Defines debug flags and debug macros under `DEBUG`.

## Dependencies and Coupling

Includes SCSI headers, `sata_defs.h`, and `sata_hba.h`. It is internal to the framework and should not be treated as an HBA driver ABI.

## Research Notes

This file is the core glue between the generic SCSI target view and SATA HBA transports. It preserves separate state machines for controller ports, port-multiplier child ports, and attached drives, while sharing event serialization flags between event processing and cfgadm operations.
