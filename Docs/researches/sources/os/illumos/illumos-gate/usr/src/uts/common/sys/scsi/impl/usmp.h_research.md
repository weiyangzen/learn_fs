# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/scsi/impl/usmp.h

## Purpose
Defines the user-level Serial Attached SCSI Management Protocol passthrough ABI.

## Main Interfaces
- `usmp_cmd_t`: request/response pointers, sizes, and timeout.
- 32-bit kernel compatibility structure and conversion macros.
- `USMPFUNC` ioctl.
- SMP request/response minimum and maximum sizes, default timeout, and SAS WWN byte size.

## Dependencies And Relationships
Includes `sys/types.h`, `sys/ioccom.h`, and `sys/scsi/generic/smp_frames.h`. Related to SAS SMP target support and the `smp` target driver.

## Research Notes
The maximum request and response size is 1032 bytes, matching SMP frame payload expectations.

## Notable Risks
- User-provided request and response pointers cross the user/kernel boundary.
- Size checks must enforce the min/max constants to avoid malformed SMP frames.
