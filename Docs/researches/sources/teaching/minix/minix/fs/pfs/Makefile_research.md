# File Research: sources/teaching/minix/minix/fs/pfs/Makefile

This makefile builds the Pipe File System service as program `pfs` from a single source file, `pfs.c`. It links against `libfsdriver` and `libsys`, then includes `<minix.service.mk>` to participate in the MINIX service build framework.
