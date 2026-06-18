# File Research: sources/os/linux/linux/fs/unicode/utf8n.h

## Purpose
Internal header for Linux filesystem UTF-8 normalization, exposing cursor APIs and generated table structures shared by runtime code, tests, and generated data.

## Main Contents
- Includes Linux types, export, string, module, and public Unicode headers.
- Declares `utf8version_is_supported()`.
- Declares `utf8nlen()` for normalized length calculation.
- Defines `UTF8HANGULLEAF`.
- Defines `struct utf8cursor`, storing:
  - map and normalization form.
  - source/decomposition scan pointers.
  - bounded lengths.
  - current and next canonical combining classes.
  - synthesized Hangul leaf buffer.
- Declares `utf8ncursor()` and `utf8byte()`.
- Defines generated table metadata:
  - `struct utf8data`
  - `struct utf8data_table`
- Declares exported `utf8_data_table`.

## Important Design Points
- This is an internal ABI between generated `utf8data.c`, normalization runtime, and tests.
- `struct utf8cursor` exposes normalization state directly to runtime code; callers initialize it with `utf8ncursor()` and consume with `utf8byte()`.
- `utf8data_table` separates age/version tables, NFDICF table metadata, NFDI table metadata, and packed trie bytes.

## Cross-File Relationships
- Included by `utf8-core.c`, `utf8-norm.c`, `mkutf8data.c` generated output, and `tests/utf8_kunit.c`.
- Depends on public `struct unicode_map` and `enum utf8_normalization` from `linux/unicode.h`.

## Risks / Review Notes
- Layout changes to `struct utf8data_table` require coordinated updates to generator output and runtime consumers.
- `UTF8HANGULLEAF` must remain large enough for the synthesized Hangul leaf used by both generator-side and runtime normalization logic.
