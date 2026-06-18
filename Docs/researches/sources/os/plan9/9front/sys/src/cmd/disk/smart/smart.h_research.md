# File Research: sources/os/plan9/9front/sys/src/cmd/disk/smart/smart.h

## Purpose
Shared declarations for the SMART monitor and transport-specific implementations.

## Key Contents
- Defines disk transport types (`Tscsi`, `Tata`) and status constants.
- `Dtype` dispatch table entries hold transport name plus probe, enable, and status callbacks.
- `Sdisk` stores linked-list state, active transport, fd, embedded `Sfis`, path/name strings, current status, silent flag, and last check/log timestamps.
- Declares ATA/SCSI probe/enable/status functions and `eprint()`.

## Notes
The embedded `Sfis` lets ATA code cache signature/features directly in each `Sdisk`, while SCSI code ignores those fields.
