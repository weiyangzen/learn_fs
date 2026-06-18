# File Research: sources/os/bsd/freebsd-src/sbin/init/Makefile

This Makefile builds the FreeBSD `init` program. It assigns `PACKAGE=runtime`, `PROG=init`, and `MAN=init.8`.

It marks the installed program as precious through `PRECIOUSPROG=`, uses backup install flags `-b -B.bak`, and adds compile definitions for `DEBUGSHELL`, `SECURE`, `LOGIN_CAP`, and `COMPAT_SYSV_INIT`.

Libraries linked are `util` and `crypt`. The file also declares the `ttys` configuration file through `CONFGROUPS= CONFTTYS`, `CONFTTYSNAME= ttys`, and `CONFTTYS+= ttys`.

Build integration is via `.include <bsd.prog.mk>`.
