# File Research: sources/os/linux/linux-stable/fs/exfat/nls.c

This file implements exFAT Unicode/NLS conversion, case folding through the upcase table, filename hash computation support, and upcase-table loading.

Key elements:
- Contains the compressed default exFAT upcase table `uni_def_upcase`, read fully and summarized here as static data implementing the recommended exFAT uppercase mapping.
- `bad_uni_chars` lists disallowed half-width ASCII filename characters for Windows compatibility.
- `exfat_convert_char_to_ucs2()` and `exfat_convert_ucs2_to_char()` bridge kernel NLS conversion and lossy replacement with `_`.
- `exfat_toupper()` maps UCS-2 values through `sbi->vol_utbl`, returning the original code point if no mapping exists.
- `exfat_uniname_ncmp()` compares UTF-16 names case-insensitively using the upcase table.
- UTF-8 paths use `utf8s_to_utf16s()`/`utf16s_to_utf8s()` when the mount is in UTF-8 mode.
- Non-UTF8 paths use NLS table conversion to/from UCS-2. UTF-16 surrogate pairs above U+FFFF are represented as `_` when converting to legacy NLS because kernel NLS is UCS-2 oriented.
- `exfat_nls_to_utf16()` computes `name_len` and the exFAT stream `name_hash` over uppercased UTF-16 bytes.
- `exfat_create_upcase_table()` scans the root directory for the upcase table entry, loads and validates it with checksum, and falls back to the default table for non-I/O validation failures.
- `exfat_free_upcase_table()` releases the table.

Important dependencies:
- Dentry hash/compare in `namei.c`, lookup matching in `dir.c`, label ioctls in `file.c`, and volume mount setup all depend on these routines.
- Checksum helpers come from `misc.c`; raw upcase dentry layout comes from `exfat_raw.h`.

Failure/edge behavior:
- Conversion failures mark names lossy and replace characters with `_`; creation rejects lossy names while lookup is more permissive for compatibility.
- Names longer than `MAX_NAME_LENGTH` return `-ENAMETOOLONG`.
- Upcase-table checksum mismatch causes fallback to the default table unless the failure was an I/O error.
