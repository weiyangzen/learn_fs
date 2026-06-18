# File Research: sources/os/plan9/9front/sys/src/cmd/scuzz/scsireq.h

Purpose: Shared SCSI request interface and constants.

Key definitions:
- `ScsiPtr`: pointer/count/write tuple for command or data transfer.
- `ScsiReq`: open target state including flags, unit path, LUN, block size, offset, fd, USB state, command/data buffers, status, sense, inquiry, and read-block flag.
- Device flags for open, sequential, read-only, WORM, changer, 6-byte mode select, 10-byte read/write, USB.
- Status constants and software status values.
- SCSI command opcode enum covering basic SCSI, MMC CD, changer, DVD, and vendor-specific commands.
- Big-endian get/put macros.

Integration: Included by all `scuzz` implementation files and referenced by USB disk/cdfs code.

Risks:
- `Umsc` is incomplete here; USB users must provide implementation.
- `GETBELONG`/`PUTBELONG` macros assume byte pointer arguments and no side effects.
