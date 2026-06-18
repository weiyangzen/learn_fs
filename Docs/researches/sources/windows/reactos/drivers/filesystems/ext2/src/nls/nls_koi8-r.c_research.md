# File Research: sources/windows/reactos/drivers/filesystems/ext2/src/nls/nls_koi8-r.c

This module registers KOI8-R as `koi8-r`, supporting Russian Cyrillic plus box-drawing symbols.

`charset2uni` maps `0x80`-`0xbf` heavily to line/box drawing and symbols, and `0xc0`-`0xff` to Russian Cyrillic in KOI8-R order. Reverse lookup uses pages `00`, `04`, `22`, `23`, and `25`.

Case conversion tables map KOI8-R Cyrillic lowercase and uppercase bytes while preserving line drawing and symbol bytes.

The public behavior is the standard NLS exact mapping API: `uni2char`, `char2uni`, lower/upper byte tables, and module registration.

Research notes: no locking or mutable state; useful as a base table for related KOI8 variants.
