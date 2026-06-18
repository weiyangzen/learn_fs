# File Research: sources/os/bsd/freebsd-src/sbin/camcontrol/timestamp.c

## Purpose
Implements `camcontrol timestamp` support for SCSI tape-drive timestamps, including reporting the device timestamp and setting it from local/UTC time or a formatted string.

## Main Elements
- `set_restore_flags()`: reads the SCSI control extension mode subpage, temporarily sets `SCEP_SCSIP` to allow SCSI timestamp changes, and restores original flags afterward.
- `report_timestamp()`: issues `REPORT TIMESTAMP`, converts the 6-byte device timestamp into a host `uint64_t` millisecond value.
- `set_timestamp()`: parses requested time, converts seconds to milliseconds, builds SCSI timestamp parameters, and issues `SET TIMESTAMP`.
- `timestamp()`: command parser for `-r`, `-s`, `-f`, `-m`, `-U`, and `-T`.

## Dependencies And Integration
Uses CAM CCB allocation/submission, SCSI helper builders from `<cam/scsi/scsi_all.h>`, and `camcontrol.h` shared command plumbing. It respects task attribute, retry count, and timeout passed from the main `camcontrol` dispatcher.

## Risk Notes
Setting timestamps temporarily changes a device control mode page and attempts restoration on exit. Time parsing uses `strptime()`/`mktime()` for formatted input, so timezone and locale behavior matter unless `-U` is used.
