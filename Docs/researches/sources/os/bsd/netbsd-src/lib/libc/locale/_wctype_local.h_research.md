# File Research: sources/os/bsd/netbsd-src/lib/libc/locale/_wctype_local.h

Read completely: 37 lines.

This header declares `_runetype_priv` and `_iswctype_priv`, the internal wide-character classification helpers.

Important interactions: included by classification, multibyte, and rune loading code that needs to query `_RuneLocale` classification data.

Security/reliability notes: declaration-only header with no direct runtime behavior.
