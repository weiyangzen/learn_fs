# File Research: sources/os/bsd/netbsd-src/sys/sys/fdio.h

Read completely: 84 lines.

## Purpose
Defines floppy disk formatting structures, options, and ioctls.

## Main Interfaces
- `enum fdformat_result`.
- `FDFORMAT_VERSION`.
- `struct fdformat_cmd`: head/cylinder command.
- `struct fdformat_parms`: geometry and formatting parameters.
- Options: `FDOPT_NORETRY`, `FDOPT_SILENT`.
- Ioctls: `FDIOCGETOPTS`, `FDIOCSETOPTS`, `FDIOCSETFORMAT`, `FDIOCGETFORMAT`, `FDIOCFORMAT_TRACK`.

## Dependencies And Integration
Uses ioctl command encoding via `sys/ioccom.h`; consumed by floppy drivers and user tools.

## Risks And Edge Cases
- Format parameter structure is versioned and should be extended only at the end.
- Driver-specific conversion is needed for transfer rates and media geometry.

## Filesystem Relevance
Low to moderate. It addresses block media below filesystems rather than filesystem logic itself.
