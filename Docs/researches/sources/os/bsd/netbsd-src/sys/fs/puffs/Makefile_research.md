# File Research: sources/os/bsd/netbsd-src/sys/fs/puffs/Makefile

This kernel include Makefile installs the public PUFFS message-interface header:

- `INCSDIR= /usr/include/fs/puffs`
- `INCS= puffs_msgif.h`
- includes `<bsd.kinc.mk>`

Its role is packaging/export, not runtime behavior. It makes `puffs_msgif.h` available to userland file servers and libraries that need the PUFFS kernel/user protocol definitions. The absence of other headers in `INCS` is significant: `puffs_sys.h` and implementation-local headers remain kernel-internal, while `puffs_msgif.h` is the ABI-facing contract.
