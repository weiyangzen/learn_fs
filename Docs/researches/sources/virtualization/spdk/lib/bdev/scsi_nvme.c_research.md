# File Research: sources/virtualization/spdk/lib/bdev/scsi_nvme.c

`scsi_nvme.c` maps NVMe completion status fields stored in a bdev I/O into SCSI status, sense key, ASC, and ASCQ values.

`spdk_scsi_nvme_translate()` switches first on NVMe status code type: generic, command specific, media error, vendor specific, and default. It then maps known NVMe status codes to SCSI good status, check condition, task aborted, reservation conflict, illegal request, medium error, hardware error, not ready, data protect, or miscompare as appropriate.

Generic mappings cover success, invalid opcode/field, data transfer or capacity errors, power-loss abort, internal device error, request/queue/fused aborts, invalid namespace/format, LBA out of range, namespace not ready, reservation conflict, and many protocol/format cases defaulting to illegal request.

Command-specific mappings cover invalid format, conflicting attributes, attempted write to read-only range, and many admin/namespace/firmware/protection cases defaulting to illegal request.

Media-error mappings distinguish write faults, unrecovered read errors, guard/app/ref tag check failures, compare failure, access denied, and default media-status cases.

Research notes: this function is policy/compatibility glue for SCSI-facing consumers of NVMe-backed bdevs. Updating it requires awareness of both NVMe status codes and SCSI sense conventions.
