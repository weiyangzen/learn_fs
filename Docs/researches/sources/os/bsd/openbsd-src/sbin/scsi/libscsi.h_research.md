# File Research: sources/os/bsd/openbsd-src/sbin/scsi/libscsi.h

This header exports the SCSI helper library used by `scsi.c`.

Key declarations:
- `SCSIREQ_ERROR(SR)`: detects sense, status, return-status, or errno-like request errors.
- Request lifecycle: `scsireq_reset`, `scsireq_new`.
- Buffer/request encode and decode visitors.
- Request builder APIs: `scsireq_build`, `scsireq_build_visit`.
- Execution/debug APIs: `scsireq_enter`, `scsi_dump`, `scsi_debug`, `scsi_debug_output`, `scsi_open`.

Integration:
- Depends on `<sys/scsiio.h>` for `scsireq_t` and SCSI ioctl definitions.
- `scsi.c` uses these declarations to construct raw commands and mode-page requests.

Risk notes:
- The header exposes low-level raw SCSI primitives; callers must supply correct command/data formats and buffer sizes.
