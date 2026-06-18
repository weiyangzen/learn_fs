# File Research: sources/os/bsd/netbsd-src/lib/libc/citrus/citrus_bcs_strtol.c

Instantiates NetBSD's shared `_strtol.h` template for BCS-only signed long parsing.

Key behavior:
- Defines `BCS_ONLY`, `_FUNCNAME` as `_bcs_strtol`, and integer bounds as `LONG_MIN`/`LONG_MAX`.
- Overrides `isspace`, `isdigit`, `isalpha`, and `isupper` to use Citrus BCS predicates.
- Includes `_strtol.h` from the common libc stdlib code.

Purpose:
- Provides locale-independent numeric parsing for Citrus config, DB text, and module version parsing.
