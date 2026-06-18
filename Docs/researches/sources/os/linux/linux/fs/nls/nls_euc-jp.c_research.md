# File Research: sources/os/linux/linux/fs/nls/nls_euc-jp.c

Purpose: Linux NLS module for Japanese EUC-JP. Unlike generated single-byte NLS modules, this converter loads the existing `cp932` NLS table and translates between Unicode, Shift-JIS/CP932, and EUC-JP forms.

Core structures and data:
- `static struct nls_table *p_nls` holds the loaded `cp932` backend.
- Shift-JIS range macros classify JIS X 0208, JIS X 0201 kana, user-defined characters, IBM extensions, and NEC/IBM extensions.
- EUC-JP range macros classify normal EUC bytes, SS2 kana, SS3 G3 blocks, and user-defined ranges.
- `sjisibm2euc_map`, `euc2sjisibm_jisx0212_map`, and `euc2sjisibm_g3upper_map` handle IBM extension mappings outside the simple SJIS/EUC arithmetic conversions.

Important behavior:
- `uni2char()` delegates Unicode-to-CP932 conversion to `cp932`, then rewrites returned Shift-JIS bytes into EUC-JP.
- `char2uni()` parses EUC-JP into temporary Shift-JIS bytes and delegates final decoding to `cp932`.
- SS2/SS3 cases can consume or emit 2 or 3 EUC bytes, with explicit output and input bound checks.
- `init_nls_euc_jp()` loads `cp932`, copies its case tables into this table, and registers charset `"euc-jp"`.

Dependencies and interfaces:
- Implements `struct nls_table` callbacks `uni2char` and `char2uni`.
- Requires `load_nls("cp932")`; init fails with `-EINVAL` if unavailable.
- Returns `-ENAMETOOLONG` for output/input length problems and `-EINVAL` for invalid or unsupported encodings.

Design notes and risks:
- The byte arithmetic relies on exact range predicates and table sizes.
- `sjisibm2euc()` assumes callers already classified the bytes as IBM Shift-JIS.
- Unsupported EUC JIS X 0212 characters deliberately fail instead of substituting a placeholder.
