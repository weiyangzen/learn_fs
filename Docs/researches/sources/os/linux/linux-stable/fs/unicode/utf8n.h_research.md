# File Research: sources/os/linux/linux-stable/fs/unicode/utf8n.h

## Summary
Internal Unicode normalization header shared by UTF-8 core, normalizer, tests, and generated data.

## Main Contents
- Declaration: `utf8version_is_supported()`.
- Normalized length API: `utf8nlen()`.
- `UTF8HANGULLEAF` size constant.
- `struct utf8cursor` normalization cursor state.
- Cursor APIs: `utf8ncursor()`, `utf8byte()`.
- Generated table descriptors: `struct utf8data`, `struct utf8data_table`.
- Exported generated table symbol: `utf8_data_table`.

## Important Behavior
`struct utf8cursor` stores the selected `unicode_map`, normalization form, current source/decomposition pointers, saved scan positions, remaining lengths, current and next canonical combining classes, and a small buffer for algorithmic Hangul decomposition.

`struct utf8data_table` groups the generated age table, NFDICF table descriptors, NFDI table descriptors, and raw trie byte array.

## Dependencies
Includes Linux Unicode public types, export/module/string headers, and is consumed by both built code and KUnit tests.

## Risks
Cursor layout is coupled to `utf8-norm.c`. Generated table structure layout is coupled to `mkutf8data.c` output and `utf8-core.c` table loading.
