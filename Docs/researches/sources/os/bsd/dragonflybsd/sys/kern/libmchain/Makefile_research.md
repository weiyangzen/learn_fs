# File Research: sources/os/bsd/dragonflybsd/sys/kern/libmchain/Makefile

Builds the `libmchain` kernel module.

Contents:
- Defines `KMOD= libmchain`.
- Defines `SRCS= subr_mchain.c`.
- Includes `<bsd.kmod.mk>`.

Filesystem relevance:
- No filesystem logic. It packages mbuf chain helper routines as a kernel module, which may support network filesystem or protocol code that serializes/deserializes messages in mbufs.
