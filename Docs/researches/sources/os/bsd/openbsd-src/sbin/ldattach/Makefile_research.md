# File Research: sources/os/bsd/openbsd-src/sbin/ldattach/Makefile

This Makefile builds `ldattach` from `ldattach.c` and `atomicio.c`, links against `libutil`, installs `ldattach.8`, enables `-Wall`, and clears `CDIAGFLAGS`.

It is a small build wrapper for the tty line-discipline attachment utility.
