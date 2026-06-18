# File Research: sources/os/bsd/netbsd-src/lib/libc/locale/_wctrans.c

Read completely: 106 lines.

This file implements `_towctrans_ext`, the extended-range wide-character translation helper. It returns `WEOF` unchanged, then binary-searches a `_WCTransEntry` extended map to translate non-cached runes.

Important interactions: `_wctrans_local.h` uses this as the slow path after cached translations. Case conversion APIs in `iswctype_mb.c` ultimately route through `_towctrans_priv`.

Security/reliability notes: assumes the `_WCTransEntry` and its range table are valid and sorted. The code comments note it assumes `wchar_t = int` when casting to `__nbrune_t`.
