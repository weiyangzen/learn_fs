# File Research: sources/os/bsd/netbsd-src/lib/libc/citrus/citrus_bcs_strtoul.c

Instantiates NetBSD's shared `_strtoul.h` template for BCS-only unsigned long parsing.

Key behavior:
- Defines `BCS_ONLY`, `_FUNCNAME` as `_bcs_strtoul`, and max value as `ULONG_MAX`.
- Redirects character classification macros to BCS predicates.
- Supports nbtool configuration includes.

Purpose:
- Used where Citrus parses unsigned fields from portable text formats, such as pivot costs.
