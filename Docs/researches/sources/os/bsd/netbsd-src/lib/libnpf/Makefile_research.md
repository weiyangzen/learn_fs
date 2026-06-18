# File Research: sources/os/bsd/netbsd-src/lib/libnpf/Makefile

Builds shared `libnpf` from `npf.c`, installs `npf.h`, and includes libnv sources from `external/bsd/libnv/lib`. It installs the `libnpf.3` manual page.

Important build details: `USE_SHLIBDIR=yes`, `WARNS=5`, and `CPPFLAGS.npf.c` adds the libnv source include path.

This library depends heavily on libnv `nvlist` serialization for its public API and kernel exchange format.
