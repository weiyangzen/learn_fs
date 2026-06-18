# File Research: sources/local-fs/e2fsprogs/lib/ext2fs/nls_utf8.c

Userspace UTF-8 normalization and casefold support adapted from Linux so ext4 casefold hashes and comparisons match kernel behavior. It includes generated Unicode trie data via `utf8data.h`.

The code validates UTF-8, looks up code point metadata through a compact trie, performs canonical decomposition, removes default-ignorable code points, handles Hangul syllable decomposition algorithmically, and emits normalized bytes ordered by canonical combining class.

Public-facing helpers load the UTF-8 12.1 table with `ext2fs_load_nls_table()`, validate names through `ext2fs_check_encoded_name()`, and compare casefolded names through `ext2fs_casefold_cmp()`.

Invalid sequences return validation errors, casefold output can fail with `-ENAMETOOLONG`, and only `EXT4_ENC_UTF8_12_1` is supported by this table.
