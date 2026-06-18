# File Research: sources/os/bsd/freebsd-src/sbin/etherswitchcfg/Makefile

Build definition for `etherswitchcfg`.

Configuration:
- `PACKAGE=runtime`
- `PROG=etherswitchcfg`
- `SRCS=etherswitchcfg.c ifmedia.c`
- Adds kernel headers include path with `CFLAGS+= -I${SRCTOP}/sys`
- Installs `etherswitchcfg.8`
- Includes `<bsd.prog.mk>`

Role:
- Builds the userspace ioctl tool for Ethernet switch device configuration.
