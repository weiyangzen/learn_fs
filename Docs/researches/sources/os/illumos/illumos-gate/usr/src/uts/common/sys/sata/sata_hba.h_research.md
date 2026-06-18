# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/sata/sata_hba.h

## Role

Public SATA HBA driver transport interface header. It defines the ABI-like structures and callbacks used by SATA HBA drivers to register with and interact with the SATA framework.

## Key Elements

- Defines success/failure/retry values and framework limits for controller ports and port-multiplier ports.
- `sata_address_t` identifies controller ports, port-multiplier ports, controllers, devices, and port multipliers through mutually exclusive qualifier bits.
- `sata_port_scr_t` holds copies of SStatus, SError, SControl, SActive, and SNotification.
- `sata_pmult_gscr_t` holds port multiplier GSCR values.
- `sata_device_t` is the framework/HBA state exchange structure for ports, devices, controllers, and port multipliers.
- Defines common, drive-specific, and port-specific state flags, plus masks for power-state classes.
- Defines SATA device type bits for ATA disk, ATAPI subtypes, port multiplier, unknown, and no device.
- `sata_cmd_t` is the full ATA/ATAPI command descriptor passed to HBA drivers, including address type, task-file registers, flags, ATAPI CDB, request-sense buffer, error-retrieval DMA handle, and DMA cookie list.
- Command flags cover data direction, queue tag type, queued command, reset-state handling, special registers, copy-out fields, and maximum queue depth.
- `sata_pkt_t` wraps `sata_device_t`, HBA/framework private pointers, operation mode, command, timeout, completion callback, and completion reason.
- Defines packet operation modes, completion reasons, error-retrieval packet types, and port-multiplier read/write packet types.
- Defines hotplug and power-management transport vectors.
- `sata_hba_tran_t` is the HBA registration vector: device info, DMA attributes, port count, feature flags, queue depth, probe/start/abort/reset/selftest callbacks, optional hotplug/power ops, and ioctl hook.
- Defines controller feature flags for ATAPI, port multiplier, hotplug, ASN, queued commands, NCQ, and FIS-based switching.
- Declares SATA framework entry points: init/fini, attach/detach, event notify, error-retrieval packets, port-multiplier helpers, DMA cleanup, and model splitting.
- Defines SATA trace ring buffer structures and trace APIs.

## Dependencies and Coupling

This is the contract consumed by HBA drivers such as `nv_sata` and `si3124`. It depends on `sata_defs.h` and DDI/SCSI kernel types.

## Research Notes

The comments are unusually detailed and encode behavioral obligations for HBA drivers: register load ordering for LBA48, completion register copy-out rules, ATAPI request-sense handling, NCQ error retrieval, reset-state semantics, and callback lifetime constraints.
