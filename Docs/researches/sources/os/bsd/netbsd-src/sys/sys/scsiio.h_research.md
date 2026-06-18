# File Research: sources/os/bsd/netbsd-src/sys/sys/scsiio.h

Read completely: 112 lines.

This header defines SCSI command and bus ioctl ABI. `scsireq_t` carries command bytes, data buffer pointer/lengths, sense buffer, status/return status, flags, timeout, and error bits. Flags indicate read/write, iovec, escape, and target operations.

It declares device ioctls for command execution, debugging, identify, deconfigure/reconfigure, and reset. Bus ioctls cover scanning, bus reset, detach, acceleration flags for sync/wide/tags, and low-level scan.

Risks: `SCIOCCOMMAND` passes a user buffer pointer through the request structure; implementation must validate direction, lengths, and copy semantics carefully.
