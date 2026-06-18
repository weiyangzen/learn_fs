# File Research: sources/os/bsd/openbsd-src/sbin/fsck_ffs/SMM.doc/Makefile

Builds the fsck_ffs SMM documentation.

Details:
- Documentation destination is `smm/03.fsck_ffs`.
- Source troff files are `0.t` through `4.t`.
- Uses `-ms` macros.
- Generates `paper.txt` by running `${ROFF} -Tascii` over the source files.
- Includes standard OpenBSD `bsd.doc.mk` rules.
