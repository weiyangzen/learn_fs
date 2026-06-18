# File Research: sources/os/linux/linux/fs/nls/nls_cp855.c

Implements Linux NLS support for codepage 855, described as Cyrillic. It provides generated single-byte conversion tables.

The forward table maps lower bytes to ASCII/control characters and the upper range to Cyrillic letters, selected symbols, and box/block drawing. Reverse Unicode coverage is sparse across pages `00`, `04`, `21`, and `25`, corresponding to Latin-1 symbols, Cyrillic, number/form symbols, and box drawing.

`uni2char()` checks output length, selects a reverse page from `page_uni2charset`, and returns `-EINVAL` when the table entry is zero. `char2uni()` maps one raw byte through `charset2uni` and rejects `0x0000`.

The module registers charset `"cp855"` with local byte casefold tables. Lifecycle is standard NLS module registration and unregistration. Metadata identifies `NLS Codepage 855 (Cyrillic)` and `Dual BSD/GPL`.
