# File Research: sources/os/bsd/netbsd-src/lib/libc/gdtoa/strtof_vaxf.c

Purpose: VAX F_floating variant of `strtof`/`strtof_l`.

Core behavior:
- Parses with a VAX-specific 24-bit `FPI`.
- Packs normal results into VAX F_floating bit layout.
- Handles no-number, zero, infinity, and sign bit placement.
- Returns `HUGE_VALF` and sets `errno` on no-memory.

Dependencies:
- Includes NetBSD namespace headers, `gdtoaimp.h`, `<locale.h>`, and `setlocale_local.h`.
- Adapted specifically for VAX floating representation.
