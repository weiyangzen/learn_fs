# File Research: sources/os/bsd/netbsd-src/lib/libukfs/Makefile

Build definition for NetBSD `libukfs`.

Key points:
- Builds library `ukfs` from:
  - `ukfs.c`
  - `ukfs_disklabel.c`
- Installs public header `ukfs.h` under `/usr/include/rump`.
- Links against:
  - `librump`
  - `librumpvfs`
  - `libpthread`
- Defines `_KERNTYPES` and includes the local directory.
- Installs manual page `ukfs.3`.

Role in subsystem:
- Builds the user-kernel filesystem access library that wraps rump filesystem operations.
