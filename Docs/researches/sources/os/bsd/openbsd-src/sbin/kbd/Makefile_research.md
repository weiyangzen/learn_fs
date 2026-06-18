# File Research: sources/os/bsd/openbsd-src/sbin/kbd/Makefile

This Makefile builds the `kbd` utility from `main.c` and `kbd_wscons.c`, installs `kbd.8`, and includes `<bsd.prog.mk>`.

It disables the program on `octeon` by setting `NOPROG=Yes`. A comment notes that architecture changes here must also be reflected in `src/distrib/special/kbd/Makefile`.
