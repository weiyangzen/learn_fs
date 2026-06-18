# File Research: sources/os/bsd/netbsd-src/lib/libpam/modules/pam_radius/Makefile

Read completely: 35 lines.

This builds `pam_radius` from `pam_radius.c`, installs `pam_radius.8`, and links against `libradius`.

A comment notes that `libradius` “doesn't exist yet” in the historical context, though the build references `${.CURDIR}/../../../libradius`.

Security/reliability notes: build-only file.
