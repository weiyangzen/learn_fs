# File Research: sources/os/bsd/netbsd-src/lib/libc/citrus/modules/citrus_mskanji.c

## Scope

Implements the Citrus ctype/stdenc module for Microsoft Kanji / Shift-JIS style encodings, including optional JIS X 0213:2004 behavior.

## APIs And Behavior

- Provides Citrus ctype and stdenc operations via `citrus_ctype_template.h` and `citrus_stdenc_template.h`.
- Maintains `_MSKanjiState` with up to two buffered bytes.
- `_citrus_MSKanji_mbrtowc_priv()` decodes single-byte ASCII/Kana or two-byte MS Kanji sequences, returning restart on incomplete byte pairs.
- `_citrus_MSKanji_wcrtomb_priv()` validates and emits one- or two-byte sequences.
- Stdenc conversion maps wide characters into csid/index classes for ISO-646, Kana, Kanji/Gaiji, and JIS2004 plane behavior.
- Module init parses variables, including JIS2004 mode.

## Dependencies

Uses Citrus ctype/stdenc templates, `_bcs` helpers, `wchar_t`, and standard errno semantics.

## Risks And Invariants

- Lead-byte and trail-byte validation is central: accepted lead ranges are `0x81-0x9f` and `0xe0-0xfc`; accepted trailing ranges are `0x40-0x7e` and `0x80-0xfc`.
- Incomplete state must preserve buffered bytes and report `(size_t)-2`.
- Stdenc row/column arithmetic differs under JIS2004 mode and must match Shift-JIS plane layout.
