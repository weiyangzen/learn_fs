# File Research: sources/os/linux/linux/fs/nls/mac-greek.c

Implements the `macgreek` NLS codepage module.

Key behavior:
- Provides generated Unicode Organization mapping tables for the Mac Greek single-byte charset.
- `charset2uni[256]` maps each input byte to Unicode; bytes `0x00` and any table entries mapped to `0x0000` are treated as invalid by `char2uni()`.
- Reverse conversion is sparse through `page_uni2charset[]`, with populated Unicode pages `00`, `01`, `03`, `20`, `21`, and `22`.
- `uni2char()` returns `-ENAMETOOLONG` if no output byte fits and `-EINVAL` when a Unicode code point has no exact Mac Greek byte.
- Registers `struct nls_table` with charset name `macgreek`.

Important interactions:
- Loaded by the NLS core through `register_nls()` / `unregister_nls()`.
- Exposes generated `charset2lower` and `charset2upper` tables, but this file’s case maps are placeholder-like rather than a rich Greek case-folding implementation.
