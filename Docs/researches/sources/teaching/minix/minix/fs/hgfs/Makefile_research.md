# File Research: sources/teaching/minix/minix/fs/hgfs/Makefile

This Makefile builds the VMware Host/Guest File System server.

Build settings:
- Program: `hgfs`.
- Source: `hgfs.c`.
- Manual page: `hgfs.8`.
- Links against `libsffs`, `libhgfs`, `libfsdriver`, and `libsys`.
- Uses `<minix.service.mk>`.

Role:
- Declares HGFS as a MINIX service wrapping shared-folder filesystem support.
