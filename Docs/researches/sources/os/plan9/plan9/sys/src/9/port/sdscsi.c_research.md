# File Research: sources/os/plan9/plan9/sys/src/9/port/sdscsi.c

Provides SCSI helper logic for `sd` storage drivers.

Key functions:
- `scsiverify`: sends INQUIRY, performs TEST UNIT READY retries, and may issue START STOP UNIT for direct-access disks.
- `scsirio`: wraps device `rio` and interprets sense data into failure/ok/no-medium/retry-style outcomes.
- `scsionline`: sends READ CAPACITY, handles retries and not-ready cases, sets unit sectors/secsize, and normalizes 2352-byte ATAPI CD blocks to 2048.
- `scsiexec`: executes an arbitrary SCSI command through the controller `rio`.
- `scsibio`: formats READ/WRITE(10) or READ/WRITE(16), issues the request, handles recovered errors/media changes/not-ready retries, and returns bytes transferred.
- `scsifmt10` and `scsifmt16` construct SCSI CDBs.

Important behavior:
- `scsiverify` tolerates `SDcheck` in some conditions as a valid detected device.
- Removable media changes clear `unit->sectors` to force a later online check.
- 16-byte commands are used for block numbers >= 2^32.

Role:
- Shared SCSI command and retry layer used by storage drivers with SCSI-like command transport.
