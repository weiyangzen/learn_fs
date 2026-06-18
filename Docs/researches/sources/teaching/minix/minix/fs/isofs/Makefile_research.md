# File Research: sources/teaching/minix/minix/fs/isofs/Makefile

This Makefile builds the ISO9660 filesystem server.

Build settings:
- Program: `isofs`.
- Sources: main/table/mount/super/inode/link/utility/path/read/SUSP/Rock Ridge/stat files.
- Links against `libfsdriver`, `libbdev`, `libsys`, and `libminixfs`.
- Adds `CPPFLAGS+= -DNR_BUFS=100`.
- Uses `<minix.service.mk>`.

Role:
- Defines isofs as a read-only MINIX fsdriver service backed by block-device and LMFS helpers.
