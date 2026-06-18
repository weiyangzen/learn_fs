# File Research: sources/os/bsd/openbsd-src/sbin/scsi/Makefile

This Makefile builds the OpenBSD `scsi` utility.

Key settings:
- `PROG=scsi`
- `SRCS=scsi.c libscsi.c`
- `MAN=scsi.8`
- Includes standard `<bsd.prog.mk>` rules.

Integration:
- Combines the CLI in `scsi.c` with SCSI request construction/debug helpers in `libscsi.c`.

Risk notes:
- No extra libraries are declared beyond the base system interfaces.
