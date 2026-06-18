# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/scsi/scsi_fm.h

## Purpose
Declares SCSI fault-management initialization, cleanup, and ereport posting helpers.

## Main Interfaces
- `scsi_fm_init(struct scsi_device *)`
- `scsi_fm_fini(struct scsi_device *)`
- `scsi_fm_ereport_post(...)` with device, path, class, ENA, devid, topology, flags, nvlist payload, and variadic payload fields.

## Dependencies And Relationships
Consumed by SCSI devices and target drivers through the kernel SCSI type include stack. Used by disk-driver FMA support in `sddef.h`.

## Research Notes
The comment asks whether init/fini should be done from child init/uninit paths, indicating it is tied to SCSI device lifecycle.

## Notable Risks
- Variadic ereport payloads require strict caller discipline.
- Incorrect path/devid/topology data can reduce fault isolation quality.
