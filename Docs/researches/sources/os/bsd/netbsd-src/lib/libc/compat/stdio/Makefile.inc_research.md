# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/stdio/Makefile.inc

Read completely: 23 lines.

This makefile fragment adds compatibility stdio sources `compat_fgetpos.c` and `compat_fsetpos.c`, including machine-architecture-specific paths. It adds stdio include flags and includes optional local make configuration when present.

Security/reliability notes: build-only; local configuration inclusion can affect build reproducibility by design.
