# File Research: sources/os/bsd/openbsd-src/sys/sys/ataio.h

Purpose: Defines ATA command and trace ioctl interfaces.

Key contents:
- `atareq_t` carries ATA command flags, command/features/register fields, data buffer pointer/length, timeout, return status, and error code.
- Command flags identify read, write, and register-read requests.
- Return status values represent OK, timeout, error, and device-fault outcomes.
- `ATAIOCCOMMAND` defines the command ioctl.
- `atagettrace_t` describes trace-buffer request/response sizing and copied/remaining counts.
- `ATAIOGETTRACE` defines the trace retrieval ioctl.

Filesystem relevance:
- Used by storage/device layers below filesystems for raw ATA command/control paths.
