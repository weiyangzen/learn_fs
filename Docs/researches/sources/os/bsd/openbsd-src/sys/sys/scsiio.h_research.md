# File Research: sources/os/bsd/openbsd-src/sys/sys/scsiio.h

Defines SCSI pass-through and debug ioctl ABI.

Key contents:
- Buffer lengths `SENSEBUFLEN` and `CMDBUFLEN`.
- `scsireq_t`: flags, timeout, command bytes/length, user data buffer and lengths, sense data, status, return status, and error.
- Command flags for read, write, iovec, escape, and target.
- Return status values: OK, timeout, busy, sense, unknown.
- Debug flags and debug ioctl.
- `struct scsi_addr` with type, bus, target, lun and type constants for SCSI/ATAPI.
- Reset/identify ioctls.
- `struct sbioc_device` and probe/detach ioctls.

Risk notes:
- Pass-through SCSI command execution requires strict validation of command length, data direction, user buffers, and privilege in implementation.
