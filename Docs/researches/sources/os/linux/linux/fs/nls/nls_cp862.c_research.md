# File Research: sources/os/linux/linux/fs/nls/nls_cp862.c

Implements Linux NLS support for codepage 862, described as Hebrew. It is a generated single-byte codepage module.

The forward table maps lower bytes to ASCII/control values. The upper range includes Hebrew letters, Latin/symbol entries, and DOS box/block drawing. Reverse lookup is sparse across pages `00`, `01`, `03`, `05`, `20`, `22`, `23`, and `25`; page `05` is the Hebrew block and is the file’s key differentiator.

`uni2char()` performs exact Unicode-to-byte conversion through `page_uni2charset` and returns `-EINVAL` for characters outside the supported mappings. `char2uni()` maps a raw byte to Unicode and rejects `0x0000`.

The `nls_table` registers charset `"cp862"` and includes local case tables, though Hebrew letters themselves are not case-paired. Init and exit register/unregister the table. Metadata is `NLS Codepage 862 (Hebrew)` and `Dual BSD/GPL`.
