# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/kiconv_utf8_euckr.h

## Purpose

`kiconv_utf8_euckr.h` is a generated-style illumos kernel conversion-data header for UTF-8 to EUC-KR. It does not implement conversion logic itself; it supplies the sorted lookup table consumed by common kernel iconv/CCK conversion routines.

## Main Data

The file defines `_SYS_KICONV_UTF8_EUCKR_H`, wraps declarations for C++ inclusion, and exposes all conversion data only under `_KERNEL`.

The kernel-only public surface is:

- `KICONV_UTF8_EUCKR_MAX (10582)`: declared mapping count.
- `static kiconv_table_t kiconv_utf8_euckr[]`: table of packed UTF-8 keys to packed EUC-KR values.

Each row is stored as two integers for `kiconv_table_t`:

- `key`: UTF-8 bytes packed into a `uint32_t`, such as `0xC2A1` or `0xED9E9D`.
- `value`: EUC-KR output bytes packed into a `uint32_t`, such as `0xA2AE` or `0xC8FE`.

Verified table properties:

- 10,582 mapping rows, matching `KICONV_UTF8_EUCKR_MAX`.
- First row: `0x0000 -> 0x003F`, a non-identical/fallback-style sentinel.
- Last row: `0xEFBFA6 -> 0xA3DC`.
- Keys are strictly ascending.
- No duplicate keys were detected.
- Packed UTF-8 key shapes: 1 sentinel row, 171 two-byte UTF-8 keys, and 10,410 three-byte UTF-8 keys.
- 2,355 keys are in the Hangul syllable UTF-8 range.
- EUC-KR output lead bytes span `0xA1..0xFD`.

The table covers symbols, punctuation, Greek, Cyrillic, kana, Hangul jamo, Hangul syllables, CJK/Hanja mappings, compatibility ideographs, fullwidth ASCII/punctuation, currency symbols, and related KS X 1001/EUC-KR repertoire entries.

## Runtime Use

There is no executable control flow in this file: no functions, branches, loops, allocation, locking, or error handling. Runtime behavior is data-driven:

1. Shared UTF-8-to-CCK conversion code validates and packs an input UTF-8 sequence.
2. EUC-KR-specific conversion code supplies `kiconv_utf8_euckr[]` and `KICONV_UTF8_EUCKR_MAX`.
3. Common lookup logic, including `kiconv_binsearch()`, searches the sorted table.
4. On a match, the packed EUC-KR value is emitted by conversion code outside this header.

## Dependencies and Related Files

`kiconv_table_t`, `kiconv_binsearch()`, `kiconv_utf8_to_cck()`, and `kiconvstr_utf8_to_cck()` are declared in `sys/kiconv_cck_common.h`.

`sys/kiconv_ko.h` defines Korean encoding helpers, including EUC-KR byte validity and EUC-KR user-defined area constants.

`sys/kiconv_euckr_utf8.h` is the reverse-direction companion table, but it is smaller: `KICONV_EUCKR_UTF8_MAX` is `8227`. This UTF-8-to-EUC-KR table has many duplicate output values, so it should not be treated as a one-to-one inverse of the reverse table.

`usr/src/uts/common/sys/Makefile` exports both `kiconv_utf8_euckr.h` and `kiconv_euckr_utf8.h` as system headers. `usr/src/uts/common/os/kiconv.c` registers the `euckr` conversion name in the broader kernel iconv framework.

## Risks and Invariants

The critical invariant is table integrity. A wrong packed key, wrong EUC-KR value, missing row, duplicate key, or sort-order break can silently corrupt Korean pathname/string conversion.

`KICONV_UTF8_EUCKR_MAX` must stay synchronized with the actual row count. Consumers using binary search depend on strict ascending key order.

Rows are packed UTF-8 byte sequences, not Unicode scalar values. Maintaining this file requires preserving the packed-byte representation expected by common kiconv code.

The table is `static` in a header, so each including translation unit can receive its own private copy. That is an established local pattern for these kiconv headers, but it means accidental writes would affect that translation unit's table copy because the array is not declared `const`.
