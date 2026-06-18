# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/kiconv_emea1.h

## Role

`kiconv_emea1.h` is a generated/static kernel header containing EMEA single-byte character-set mapping tables for illumos kernel iconv support. It has no executable functions; its behavior is entirely data-driven through two arrays used by the single-byte-to-UTF-8 and UTF-8-to-single-byte conversion paths.

The file covers 24 encodings: CP737, CP852, CP857, CP862, CP866, CP1250, CP1251, CP1253, CP1254, CP1255, CP1256, CP1257, ISO-8859-2, ISO-8859-3, ISO-8859-4, ISO-8859-5, ISO-8859-6, ISO-8859-7, ISO-8859-8, ISO-8859-9, ISO-8859-10, ISO-8859-11/TIS-620, ISO-8859-13, and KOI8-R.

## Major Definitions

The header is protected by `_SYS_KICONV_EMEA1_H`, exposes C linkage for C++ consumers, includes `<sys/kiconv.h>`, and only declares table data under `_KERNEL`.

It defines:
- `static const kiconv_to_utf8_tbl_comp_t to_u8_tbl[24][128]`
- `static const kiconv_to_sb_tbl_comp_t to_sb_tbl[24][128]`

`to_u8_tbl` maps each non-ASCII byte in a source encoding to UTF-8 bytes. The runtime index is `single_byte - 0x80`, so each subtable has exactly 128 entries for byte values `0x80` through `0xFF`.

`to_sb_tbl` maps packed UTF-8 byte sequences back to the matching single-byte value. Each subtable is sorted by the 24-bit packed UTF-8 key so the conversion implementation can use binary search.

## Data Shape

The forward table contains 3,072 entries total: 24 subtables times 128 high-half single-byte values. A whole-file structural pass found 2,391 two-byte UTF-8 mappings, 510 three-byte UTF-8 mappings, and 171 invalid/unassigned forward slots represented by `{ 0xFE, 0xFE, 0xFE }`.

Invalid forward slots appear only in encodings with unassigned bytes: CP857, CP1250, CP1251, CP1253, CP1254, CP1255, CP1257, ISO-8859-3, ISO-8859-6, ISO-8859-7, ISO-8859-8, and ISO-8859-11. Encodings such as CP737, CP852, CP862, CP866, CP1256, ISO-8859-2, ISO-8859-4, ISO-8859-5, ISO-8859-9, ISO-8859-10, ISO-8859-13, and KOI8-R have no invalid forward slots in this table.

The reverse table also contains 3,072 entries total. Each of the 24 reverse subtables has 128 entries and is non-descending by packed UTF-8 key. Subtables with invalid/unassigned byte slots use repeated `0xFFFFFF -> 0x00` filler entries near the end; those repeated keys preserve array width but are not real Unicode mappings.

## Runtime Use

The common illumos `kiconv` single-byte conversion logic uses this table family as follows:
- For source single-byte to UTF-8, ASCII bytes below `0x80` are copied directly; high-half bytes index `to_u8_tbl[id][byte - 0x80]`.
- The first stored UTF-8 byte is passed through `u8_number_of_bytes[]` to decide whether the entry is valid and how many bytes to copy.
- Invalid forward entries produce `EILSEQ` in normal conversion paths, or the UTF-8 replacement character in `kiconvstr` paths when `KICONV_REPLACE_INVALID` is requested.
- For UTF-8 to a single-byte target, the implementation validates UTF-8 input, packs the byte sequence into a 24-bit key, and binary-searches the corresponding `to_sb_tbl[id]` subtable.
- If no reverse mapping is found, conversion writes the ASCII replacement character and increments the non-identical conversion count.

The central code-list in `usr/src/uts/common/os/kiconv.c` assigns the relevant EMEA code ids from `18` through `42`; this header supplies all of those EMEA mappings except CP720, which is kept in `kiconv_emea2.h`.

## Dependencies

This file depends on the table component types in `sys/kiconv.h`:
- `kiconv_to_utf8_tbl_comp_t`, a three-byte UTF-8 byte array.
- `kiconv_to_sb_tbl_comp_t`, a packed 24-bit UTF-8 key plus 8-bit single-byte output.

Runtime correctness also depends on UTF-8 validation tables supplied outside this header, including `u8_number_of_bytes[]`, `u8_valid_min_2nd_byte[]`, and `u8_valid_max_2nd_byte[]`.

`usr/src/uts/common/sys/Makefile` lists `kiconv_emea1.h` as an exported kernel header.

## Maintenance Notes

The subtable order is part of the implicit ABI between code-page ids and table ids. Adding, removing, or reordering encodings requires coordinated updates to the EMEA module id mapping.

Every forward subtable must remain exactly 128 entries because high-half single-byte input is converted by direct array indexing. Every reverse subtable must remain sorted by packed UTF-8 key because lookup uses binary search. Placeholder invalid entries should remain distinguishable from valid UTF-8 so the conversion code reports or replaces invalid source bytes correctly.
