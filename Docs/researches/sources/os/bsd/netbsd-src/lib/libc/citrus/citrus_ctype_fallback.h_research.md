# File Research: sources/os/bsd/netbsd-src/lib/libc/citrus/citrus_ctype_fallback.h

Declares fallback ctype functions used to bridge older module ABI versions.

Key behavior:
- Declares ABI v2 fallbacks: `_citrus_ctype_btowc_fallback`, `_citrus_ctype_wctob_fallback`.
- Declares ABI v3 fallbacks: `_citrus_ctype_mbsnrtowcs_fallback`, `_citrus_ctype_wcsnrtombs_fallback`.

This header is included by ctype local definitions and the dynamic module initialization logic.
