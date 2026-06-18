# File Research: sources/teaching/minix/minix/fs/vbfs/Makefile

Build file for the VirtualBox Shared Folders filesystem server.

Key contents:
- Builds program `vbfs` from `vbfs.c`.
- Installs manual page `vbfs.8`.
- Installs `vbfs.conf` as `/etc/system.conf.d/vbfs`.
- Links against `libsffs`, `libvboxfs`, `libfsdriver`, and `libsys`.
- Uses `<minix.service.mk>`, meaning it is built and installed as a MINIX service.
