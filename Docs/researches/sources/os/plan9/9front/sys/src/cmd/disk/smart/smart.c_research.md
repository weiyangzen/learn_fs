# File Research: sources/os/plan9/9front/sys/src/cmd/disk/smart/smart.c

## Purpose
Main program for periodic SMART/health monitoring across ATA and SCSI disks.

## Key Behavior
- Supports explicit disk paths or auto-probing `/dev/sdctl`; `-p` probes in addition to explicit paths, `-a` logs all devices, `-t` runs in test/foreground mode, and `-v` enables verbose stderr output.
- Opens each candidate `path/raw`, tries ATA and SCSI probe/enable dispatch entries, and records supported disks in a linked list.
- Periodically checks each disk at `Checksec` intervals, reopening only for the check and closing afterward.
- Logs prolonged open failures, health status changes, repeated failures after a relog interval, and optionally all new/status messages.
- In test mode, exits after one run with failure status if any disk reports an error.
- Uses `/dev/sdctl` controller names to probe `/dev/<controller><hex-unit>` candidates until devices stop existing.

## Interfaces And Dependencies
- Uses `Dtype` implementations from `ata.c` and `scsi.c`.
- Uses Plan 9 `syslog()` unless in test mode.

## Notes
The program is a long-running monitor by default, sleeping 30 seconds between scheduler passes while each disk has a 10-minute check interval.
