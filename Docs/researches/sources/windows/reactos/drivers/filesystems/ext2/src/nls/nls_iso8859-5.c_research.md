# File Research: sources/windows/reactos/drivers/filesystems/ext2/src/nls/nls_iso8859-5.c

This module registers ISO-8859-5 as `iso8859-5`, providing Cyrillic charset conversion.

`charset2uni` maps the upper half of the byte range to Cyrillic U+0400/U+0410/U+0430 ranges plus symbols such as numero sign. Reverse mapping uses `page00`, `page04`, and `page21`.

The lower/upper tables encode Cyrillic case conversion in charset-byte space, including uppercase Cyrillic letters at `0xb0`-style positions and lowercase counterparts at `0xd0`/`0xe0`.

`uni2char` checks `boundlen <= 0`, then maps through page tables. `char2uni` rejects `0x0000` table results.

Research notes: table-driven; no special handling for locale-specific Cyrillic case behavior beyond the static ISO-8859-5 table.
