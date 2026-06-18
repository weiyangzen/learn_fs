# File Research: sources/os/bsd/netbsd-src/sys/sys/ataio.h

Read completely: 56 lines.

Defines ATA command and ATA bus ioctl interfaces.

Key elements:
- `atareq_t` carries ATA command flags, command/features/sector/head/cylinder fields, user data buffer pointer and length, timeout, returned status, and error bits.
- Command flags indicate read, write, register read, and LBA addressing.
- Return statuses distinguish OK, timeout, command error, and device fault.
- `ATAIOCCOMMAND` is an `_IOWR('Q', 8, atareq_t)` ioctl for issuing ATA commands.
- ATA bus ioctls support scanning for devices, resetting the bus, and detaching a selected or wildcard device.

Risks and notes:
- This is a low-level user/kernel ioctl ABI exposing raw ATA command fields.
- Incorrect callers can request destructive device operations; validation is expected in ioctl handlers outside this header.
