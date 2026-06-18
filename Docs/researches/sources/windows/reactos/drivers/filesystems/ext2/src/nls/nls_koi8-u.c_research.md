# File Research: sources/windows/reactos/drivers/filesystems/ext2/src/nls/nls_koi8-u.c

This module registers KOI8-U as `koi8-u`, supporting Ukrainian Cyrillic additions over KOI8-R.

The table includes KOI8 line-drawing symbols and Cyrillic mappings, plus Ukrainian characters such as IE, I, YI, and GHE with upturn. Reverse lookup uses the same broad pages as KOI8-R with additional U+0490/U+0491 coverage.

Case conversion tables account for the Ukrainian additions and standard Cyrillic byte-pair casing.

It exposes the standard NLS callbacks and is also a runtime dependency for `nls_koi8-ru.c`.

Research notes: static exact mapping table; no dynamic behavior after registration.
