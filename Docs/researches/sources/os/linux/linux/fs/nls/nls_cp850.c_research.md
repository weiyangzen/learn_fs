# File Research: sources/os/linux/linux/fs/nls/nls_cp850.c

Implements Linux NLS support for codepage 850, described as Europe. The file supplies generated exact translation tables for a DOS/OEM Western European encoding.

`charset2uni[256]` maps low bytes to ASCII/control values and high bytes to Western European Latin letters, symbols, and DOS line/block drawing characters. Reverse Unicode pages are `00`, `01`, `20`, and `25`, covering Latin-1, limited Latin Extended-A, selected punctuation/currency, and box/block drawing.

`uni2char()` performs a sparse reverse-table lookup and returns `-ENAMETOOLONG` for no output capacity or `-EINVAL` for unmappable Unicode. `char2uni()` performs direct byte lookup and rejects mappings resolving to `0x0000`.

The registered `nls_table` is named `"cp850"` and includes charset-local lower/upper maps used by filesystems that need codepage-aware case behavior. Init and exit register/unregister this table. Metadata is `NLS Codepage 850 (Europe)` under `Dual BSD/GPL`.
