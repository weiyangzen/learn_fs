# File Research: sources/os/bsd/openbsd-src/sbin/init/Makefile

This OpenBSD makefile builds the `init` program.

Key contents:
- `PROG= init`
- Installs/associates `init.8` man page.
- Links against `libutil` via `DPADD=${LIBUTIL}` and `LDADD=-lutil`.
- Adds `-DDEBUGSHELL -DSECURE` to `CFLAGS`, enabling alternate-shell prompt support and secure single-user password checks.
- Includes `<bsd.prog.mk>`.

Relevance:
- The compile-time flags directly enable branches in `init.c` for debug shell selection and root password validation before single-user shell access on insecure console settings.
