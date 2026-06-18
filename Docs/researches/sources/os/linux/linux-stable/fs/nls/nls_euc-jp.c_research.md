# File Research: sources/os/linux/linux-stable/fs/nls/nls_euc-jp.c

Purpose: Linux NLS module for Japanese EUC-JP. Unlike most single-byte NLS table files, this module is a converter layered on top of the existing `cp932` NLS implementation, translating between Unicode and Shift-JIS/CP932 first and then between Shift-JIS and EUC-JP.

Core structures and data:
- `static struct nls_table *p_nls` holds the loaded `cp932` backend.
- Macros classify Shift-JIS byte ranges: JIS X 0208, JIS X 0201 kana, user-defined character ranges, IBM extended ranges, and NEC/IBM extension ranges.
- Macros classify EUC-JP byte sequences: normal EUC bytes, SS2 kana, SS3 G3 block, and user-defined ranges.
- `sjisibm2euc_map`, `euc2sjisibm_jisx0212_map`, and `euc2sjisibm_g3upper_map` encode IBM extended character conversions that are not expressible by the simple arithmetic SJIS/EUC transforms.

Important behavior:
- `uni2char()` delegates Unicode-to-byte conversion to `cp932`, then rewrites returned Shift-JIS bytes into EUC-JP. It handles one-byte kana by adding SS2, two-byte JIS X 0208 arithmetic conversion, UDC low/high ranges, IBM extensions, and NEC/IBM extension normalization.
- `char2uni()` parses EUC-JP input into a temporary Shift-JIS sequence and delegates final byte-to-Unicode conversion to `cp932`. It rejects unsupported JIS X 0212 or invalid EUC forms with `-EINVAL`.
- SS3-based high UDC and IBM extended sequences may consume or emit 3 EUC bytes, so both conversion directions include explicit bound checks.
- `init_nls_euc_jp()` loads `cp932`, copies its upper/lower tables into the public `nls_table`, then registers charset `"euc-jp"`.
- `exit_nls_euc_jp()` unregisters the table and unloads `cp932`.

Dependencies and interfaces:
- Implements the kernel `struct nls_table` callbacks `uni2char` and `char2uni`.
- Depends on `load_nls("cp932")`; failure to load that charset makes module init return `-EINVAL`.
- Uses Linux errno semantics: `-ENAMETOOLONG` for output buffer exhaustion and `-EINVAL` for invalid/unrepresentable encodings.

Design notes and risks:
- The conversion code is byte-arithmetic-heavy and relies on static table sizes and range macros matching the CP932/EUC mapping assumptions.
- `sjisibm2euc()` indexes into `sjisibm2euc_map` after the caller classifies the bytes as IBM Shift-JIS; callers must preserve that precondition.
- Unsupported EUC JIS X 0212 characters deliberately fail instead of substituting a GETA marker, as shown by the commented-out fallback in `char2uni()`.
