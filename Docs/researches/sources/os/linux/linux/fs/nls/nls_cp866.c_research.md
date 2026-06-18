# File Research: sources/os/linux/linux/fs/nls/nls_cp866.c

Implements Linux NLS support for codepage 866, described as Cyrillic/Russian. It is generated and exact-mapping-only.

The byte-to-Unicode table maps low bytes to ASCII/control values, high bytes mostly to Cyrillic uppercase/lowercase letters, plus selected symbols and box/block drawing. Reverse Unicode pages are `00`, `04`, `21`, `22`, and `25`, covering Latin-1 symbols, Cyrillic, number/form symbols, math, and drawing characters.

`uni2char()` performs the standard reverse lookup with `-ENAMETOOLONG` for no space and `-EINVAL` for unmappable Unicode. `char2uni()` maps one byte and rejects `0x0000`.

The `nls_table` charset is `"cp866"` and includes Cyrillic-aware byte case maps. Lifecycle functions register/unregister the table. Metadata is `NLS Codepage 866 (Cyrillic/Russian)` and `Dual BSD/GPL`.
