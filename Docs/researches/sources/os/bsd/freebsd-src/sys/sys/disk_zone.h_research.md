# File Research: sources/os/bsd/freebsd-src/sys/sys/disk_zone.h

## Purpose
Defines the generic ioctl payloads and constants for zoned block devices using SCSI ZBC or ATA ZAC semantics.

## Main Elements
- `disk_zone_disk_params` reports zone mode, supported commands, optimal/max open/sequential zone counts.
- `disk_zone_rwp` describes reset-write-pointer/open/close/finish targets and all-zones flag.
- `disk_zone_rep_header` and `disk_zone_rep_entry` describe report-zones output.
- `disk_zone_report` carries report request options, entry allocation/fill counts, and user entry pointer.
- `disk_zone_args` selects zone command: open, close, finish, report, reset write pointer, get params.
- Constants define zone modes, feature flags, same-layout values, zone types, conditions, flags, and report filters.

## Dependencies And Integration
Included by `sys/disk.h` for `DIOCZONECMD` and consumed by zoned disk drivers and tools.

## Risk Notes
The entry pointer and counts cross the ioctl boundary. Kernel handlers must carefully bound copyin/copyout and account for future SCSI/ATA values not yet named here.
