# File Research: sources/os/plan9/9front/sys/src/9/port/sdscsi.c

Shared SCSI helper layer for Plan 9 `sd` device drivers.

Key responsibilities:
- Verifies a SCSI unit by issuing INQUIRY and TEST UNIT READY, with not-ready/no-medium handling.
- Attempts START STOP UNIT for direct-access devices to spin up disks after successful readiness checks.
- Reads capacity using READ CAPACITY(10), falling back to READ CAPACITY(16) for large devices.
- Normalizes device geometry, including converting returned last-LBA to sector count and fudging ATAPI 2352-byte sectors to 2048.
- Builds READ(10)/WRITE(10) or READ(16)/WRITE(16) CDBs for block I/O.
- Provides retry/error classification for common sense keys and ASC/ASCQ cases.
- Detects removable-media change and clears `unit->sectors` to force re-online.

Dependencies:
- Calls the concrete device interface through `unit->dev->ifc->rio`.
- Uses Plan 9 `SDreq`, `SDunit`, status constants, sense flags, and shared allocation helpers.

Notable behavior:
- `scsionline()` retries capacity reads up to 10 times and returns `ok + retries`, preserving retry information in the status value.
- `scsibio()` turns SCSI sense data into Plan 9 errors containing sense key/ASC/ASCQ and sector number.
- The code comments note LUN handling as questionable in several CDB fields.
