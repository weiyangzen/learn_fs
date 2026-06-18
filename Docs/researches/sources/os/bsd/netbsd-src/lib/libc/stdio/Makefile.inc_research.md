# File Research: sources/os/bsd/netbsd-src/lib/libc/stdio/Makefile.inc

Read completely: 78 lines.

This make include adds the NetBSD libc stdio implementation sources and associated manuals. It lists core byte and wide I/O files, memory-stream files, formatted I/O, scanf/printf locale variants, temporary-file helpers, and compatibility exclusions under `AUDIT`.

Important interactions: controls which stdio objects are built into libc and installs extensive manpage links for related APIs.

Security/reliability notes: no runtime logic, but build inclusion here defines the exported stdio surface.
