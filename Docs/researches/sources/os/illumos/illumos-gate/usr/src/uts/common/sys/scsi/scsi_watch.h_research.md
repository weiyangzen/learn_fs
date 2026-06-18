# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/scsi/scsi_watch.h

## Purpose
Declares SCSI watch service interfaces for periodic device polling and media monitoring.

## Main Interfaces
- `struct scsi_watch_result`: status, sense, actual sense length, MMC data, and packet.
- `SCSI_WATCH_IO_TIME`
- Termination flags and result constants.
- Functions: `scsi_watch_init`, `scsi_watch_fini`, `scsi_watch_request_submit`, `scsi_mmc_watch_request_submit`, `scsi_watch_request_terminate`, `scsi_watch_get_ref_count`, `scsi_watch_resume`, `scsi_watch_suspend`.

## Dependencies And Relationships
Used by disk and tape target drivers for media state monitoring. Types come through the SCSI include stack.

## Research Notes
Default watch I/O timeout is 120 seconds to support slow devices.

## Notable Risks
- Watch tokens carry lifecycle and reference-count concerns across suspend/resume and detach.
- Termination may be synchronous or asynchronous depending on flags.
