# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/scsi/impl/uscsi.h

## Purpose
Defines the user-level SCSI passthrough ioctl ABI and kernel helper interfaces for translating `uscsi_cmd` requests into SCSI packets.

## Main Interfaces
- `struct uscsi_cmd`: flags, status, timeout, CDB pointer, data buffer, lengths, residuals, request-sense buffer, and path instance.
- 32-bit syscall compatibility structure and conversion macros under `_SYSCALL32`.
- `USCSI_*` flags for read/write, reset, request sense, queue tags, path selection, PM failfast, and legacy parallel SCSI controls.
- `struct uscsi_rqs`, `RQS_OVR`, `RQS_VALID`.
- Ioctls: `USCSICMD`, `USCSIMAXXFER`.
- Kernel helpers: `scsi_uscsi_copyin`, `scsi_uscsi_pktinit`, `scsi_uscsi_handle_cmd`, `scsi_uscsi_pktfini`, copyout/free helpers.

## Dependencies And Relationships
Included by implementation SCSI types and used by target drivers such as disk, tape, generic SCSI, and SES for user passthrough and internal command handling.

## Research Notes
Some flags are explicitly not for user level, including `USCSI_NOINTR`, queue tag controls, and parallel bus controls.

## Notable Risks
- This is a user/kernel ABI; field sizes and 32-bit conversion behavior must remain compatible.
- Passthrough can issue destructive SCSI commands; validation and reserved-bit handling are important.
- `USCSI_PATH_INSTANCE` interacts with MPxIO path selection and must not accidentally pin retries to failed paths.
