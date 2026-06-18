# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/fm/io/disk.h

This small header defines disk-related FMA fault class names.

Primary class:
- `DISK_ERROR_CLASS` is `"io.disk"`.

Fault classes:
- `FM_FAULT_DISK_PREDFAIL` for predictive failure.
- `FM_FAULT_DISK_OVERTEMP` for over-temperature.
- `FM_FAULT_DISK_TESTFAIL` for self-test failure.
- `FM_FAULT_SSM_WEAROUT` for solid-state media wearout.

Dependencies and relationships:
- Complements SCSI transport ereports in `sys/fm/io/scsi.h`.
- Used by disk diagnosis/reporting components to classify diagnosed disk faults.
