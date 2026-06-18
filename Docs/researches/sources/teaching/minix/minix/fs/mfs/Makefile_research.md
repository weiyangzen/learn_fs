# File Research: sources/teaching/minix/minix/fs/mfs/Makefile

This makefile builds the MINIX File System service as program `mfs`. It lists the service implementation sources: cache, link, mount, misc, open, protect, read, stadir, stats, table, time, utility, write, inode, main, path, and super.

The service links against MINIX filesystem support libraries: `libminixfs`, `libfsdriver`, `libbdev`, and `libsys`. `CPPFLAGS` sets `DEFAULT_NR_BUFS=1024`, which is consumed during MFS initialization to size the libminixfs buffer pool. The final include, `<minix.service.mk>`, integrates the program into the MINIX service build framework.
