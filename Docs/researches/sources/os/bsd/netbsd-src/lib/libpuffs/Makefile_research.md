# File Research: sources/os/bsd/netbsd-src/lib/libpuffs/Makefile

This makefile builds the NetBSD `libpuffs` library. It includes `bsd.own.mk`, enables `_FORTIFY_SOURCE` by default through `USE_FORT?= yes`, sets `WARNS?= 5`, names the library `puffs`, lists implementation sources, installs manual pages, and installs `puffs.h` and `puffsdump.h` under `/usr/include`.

The source list includes the files in this group plus broader library components such as `puffs.c`, `null.c`, `opdump.c`, `paths.c`, `pnode.c`, `requests.c`, `subr.c`, and `suspend.c`. Lint flags suppress some warnings, and `callcontext.c` receives a GCC 12-specific `-Wno-dangling-pointer` because it intentionally manipulates stack/context pointers in ways that confuse the compiler warning.

Integration points: defines build membership for the userspace filesystem support library. Risks are warning suppression hiding real context-lifetime bugs and the source list being the authoritative compilation boundary for libpuffs behavior.
