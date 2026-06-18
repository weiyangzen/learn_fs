# File Research: sources/os/linux/linux/fs/nls/nls_cp437.c

Implements Linux NLS support for DOS/OEM codepage 437, described as United States/Canada. The file is a generated translation module based on Unicode Organization charset data and only exposes exact Unicode-to-charset mappings.

The main data path is `charset2uni[256]`, mapping each single-byte CP437 value to `wchar_t`. Bytes `0x00-0x7f` are mostly ASCII/control values, while `0x80-0xff` include Latin accented letters, currency symbols, Greek/math symbols, block drawing, and box drawing characters. Reverse mapping is implemented through sparse `pageXX[256]` tables for Unicode high-byte pages `00`, `01`, `03`, `20`, `22`, `23`, and `25`, referenced by `page_uni2charset`.

`uni2char()` rejects zero output space with `-ENAMETOOLONG`, indexes the reverse page by Unicode high and low bytes, returns `-EINVAL` when no exact mapping exists, and writes one byte on success. `char2uni()` maps one input byte through `charset2uni` and treats a resulting `0x0000` as invalid, so byte NUL/undefined mappings are not accepted as regular characters by this callback.

The module exports `struct nls_table table` with charset `"cp437"`, the two conversion callbacks, and CP437-specific `charset2lower`/`charset2upper` tables. Initialization registers the table; exit unregisters it. Module metadata is `NLS Codepage 437 (United States, Canada)` with `Dual BSD/GPL`.
