# File Research: sources/teaching/minix/minix/lib/libminixfs/Makefile

Build file for `libminixfs`.

Key contents:
- Includes `<bsd.own.mk>`.
- Adds `-D_MINIX_SYSTEM` to `CPPFLAGS`.
- Builds library `minixfs`.
- Library sources are `cache.c` and `bio.c`.
- Includes `<bsd.lib.mk>`.

This library provides reusable MINIX filesystem support, mainly buffer-cache and block I/O helpers.
