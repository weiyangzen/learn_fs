# File Research: sources/os/linux/linux/fs/nls/nls_cp857.c

Implements Linux NLS support for codepage 857, described as Turkish. It is a generated exact mapping module.

The byte-to-Unicode table maps ASCII/control values in the lower half and Turkish/Western Latin characters plus box drawing in the upper half. Reverse Unicode mappings are provided for pages `00`, `01`, and `25`, covering Latin-1, limited Latin Extended-A Turkish characters, and box/block drawing.

`uni2char()` uses the common two-level reverse lookup and returns one byte on success, `-ENAMETOOLONG` for no output buffer, or `-EINVAL` for unmappable Unicode. `char2uni()` maps one input byte and rejects a `0x0000` result.

The `nls_table` charset is `"cp857"`, with codepage-specific `charset2lower` and `charset2upper` tables. Init/exit register and unregister the table. Metadata is `NLS Codepage 857 (Turkish)` and `Dual BSD/GPL`.
