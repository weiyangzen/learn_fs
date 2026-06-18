# File Research: sources/os/bsd/netbsd-src/lib/libc/gdtoa/Makefile.inc

Build fragment for David M. Gay's gdtoa floating-point conversion code in libc. It adds include paths for local gdtoa and locale headers, sets floating-rounding or VAX-specific preprocessor flags, requires architecture-specific `arith.h` and `gd_qnan.h`, and includes `${ARCHDIR}/gdtoa/Makefile.inc` for machine-dependent conversion module selection.

It appends public and private conversion sources such as `strtod.c`, `dtoa.c`, `ldtoa.c`, `hdtoa.c`, `gdtoa.c`, locking, hexadecimal parsing/formatting, miscellaneous bigint support, `strtodg.c`, and `strtord.c` on non-VAX architectures. Lint flags suppress known conversion warnings in selected files.

Dependencies: machine architecture make fragments and headers are required to choose float/long-double formats.

Risks/invariants: correct conversion behavior depends on matching architecture arithmetic headers and selected source variants to actual ABI floating-point formats.
