# File Research: sources/os/bsd/dragonflybsd/sys/sys/mtio.h

Magnetic tape ioctl ABI and status definitions.

Key responsibilities:
- Defines `struct mtop` for tape operation commands and repeat counts.
- Enumerates tape operations such as write EOF, file/record spacing, rewind, offline, cache control, block size, density, erase, EOD, compression, retension, and setmark operations.
- Defines DragonFly-specific compression status constants and drive-state `mt_dsreg` values.
- Defines `struct mtget` for tape status, position, density, block size, compression, and mode-specific settings.
- Defines SCSI tape error status structures and reserved union padding.
- Enumerates legacy tape controller/device type constants.
- Defines tape ioctls for operations, status, logical/hardware position, locate, error stats, and EOT model control.
- Defines default tape path for userland and kernel minor-device bit masks.

Important behavior:
- `MTIOCERRSTAT` returns latched SCSI sense data and clears it.
- `mt_resid` is noted as potentially nonsensical for large residuals; detailed residuals are available through error status.
- DragonFly extends the historical BSD tape ABI with block size, density, compression, and state fields.

Dependencies:
- Includes `sys/types.h` and `sys/ioccom.h`.

Notable risks:
- Structure layout and ioctl numbers are userland ABI.
- Some fields are reserved or explicitly not implemented but preserved for compatibility.
- Older 32-bit residual fields are inadequate for large tape I/O.
