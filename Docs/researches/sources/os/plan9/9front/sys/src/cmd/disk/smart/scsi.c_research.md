# File Research: sources/os/plan9/9front/sys/src/cmd/disk/smart/scsi.c

## Purpose
Implements SCSI health probing, enabling, and status checks for `disk/smart`.

## Key Behavior
- Builds SCSI CDBs for test-unit-ready, request-sense, mode-sense(10), and mode-select(10).
- `issuescsi()` writes the CDB, performs the data phase, reads sd status, and on nonzero status issues request sense to capture detailed sense bytes.
- `scsiprobe()` verifies SCSI command support with TUR and confirms the Informational Exceptions mode page (`0x1c`) is readable.
- `scsienable()` writes mode page `0x1c` to enable background functions, warnings, logging, and request-sense-only reporting.
- `scsistatus()` requests sense and reports `normal` when ASC/ASCQ are zero, otherwise maps them through `scsierror()`.

## Interfaces And Dependencies
- Uses Plan 9 scuzz SCSI definitions from `/sys/src/cmd/scuzz/scsireq.h`.
- Called through `smart.c`'s `Dtype` dispatch table.

## Notes
This path uses SCSI informational exceptions rather than ATA SMART return-status semantics. Sense tracing code exists but is disabled.
