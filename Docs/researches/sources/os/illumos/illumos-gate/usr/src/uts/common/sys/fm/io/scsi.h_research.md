# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fm/io/scsi.h

This header defines SCSI disk-transport FMA ereport names and payload fields.

Primary classes:
- `SCSI_ERROR_CLASS` is `"io.scsi"`.
- `SCSI_DISK_CLASS` is `"disk"`.

Ereport types:
- Predictive failure with ASC/ASCQ payload fields.
- Over-temperature with current and threshold temperature payload fields.
- Solid-state media wearout with current and threshold wearout fields.
- Self-test failure with result code, address, timestamp, and segment fields.

Dependencies and relationships:
- Intended for userland disk-transport modules reporting disk-originated SCSI errors.
- Complements diagnosed disk fault names in `sys/fm/io/disk.h`.
