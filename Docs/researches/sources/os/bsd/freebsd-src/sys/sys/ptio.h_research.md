# File Research: sources/os/bsd/freebsd-src/sys/sys/ptio.h

Read completely: 37 lines.

## Purpose
Defines CAM passthrough timeout ioctl numbers.

## Main Elements
- Includes `sys/ioccom.h`.
- Defines `PTIOCGETTIMEOUT` as an integer read ioctl.
- Defines `PTIOCSETTIMEOUT` as an integer write ioctl.

## Dependencies And Integration
Used by passthrough device interfaces that expose timeout configuration via ioctl.

## Risk Notes
The ioctl group/number/type are user ABI; changing them would break existing callers.
