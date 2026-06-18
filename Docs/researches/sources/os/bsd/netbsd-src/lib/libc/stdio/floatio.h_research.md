# File Research: sources/os/bsd/netbsd-src/lib/libc/stdio/floatio.h

Read completely: 55 lines.

This private header defines buffer sizing constants for floating-point scanf/printf conversion: `MAXEXP`, `MAXFRACT`, and `MAXEXPDIG`. It includes a compile-time check that `LDBL_MAX_EXP` remains within the assumed exponent digit budget.

Important interactions: used by formatted I/O conversion code outside this group.

Security/reliability notes: correctness depends on these constants being large enough for all supported long-double formats.
