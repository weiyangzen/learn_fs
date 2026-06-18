# File Research: sources/os/bsd/netbsd-src/lib/libterminfo/Makefile

Build definition for NetBSD `libterminfo`.

Key points:
- Builds shared library `terminfo` from `term.c`, `ti.c`, `setupterm.c`, `curterm.c`, `tparm.c`, `tputs.c`, generated `hash.c`, and termcap compatibility sources.
- Installs public headers `term.h` and `termcap.h`.
- Enables optional full-featured behavior unless `SMALLPROG` is defined:
  - `TERMINFO_COMPILE`
  - `TERMINFO_DB`
  - `TERMINFO_COMPAT`
  - Adds `compile.c`.
- Includes generated hash build rules via `Makefile.hash`.
- Generates `terminfo.5` from `genman`, `terminfo.5.in`, `term.h`, and `termcap_map.c`.
- Provides compatibility symlinks for `libtermcap` and `libtermlib` archives and shared objects pointing to `libterminfo`.

Role in subsystem:
- Central build orchestration for the terminfo implementation, compatibility ABI, generated lookup tables, and generated manual page.
