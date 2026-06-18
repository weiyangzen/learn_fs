# File Research: sources/os/bsd/netbsd-src/lib/libc/locale/dummy_lc_collate.c

Read completely: 53 lines.

This file instantiates the dummy locale-category template for `LC_COLLATE`. It defines `_PREFIX`, `_CATEGORY_ID`, and `_CATEGORY_NAME`, then includes `dummy_lc_template.h`.

Important interactions: `setlocale.c` registers `_dummy_LC_COLLATE_setlocale` for `LC_COLLATE`. Since real collation is not implemented here, wide collation functions also fall back to simple string behavior.

Security/reliability notes: only accepts C/POSIX or environment-resolved values through the template. No file loading or dynamic allocation beyond template behavior.
