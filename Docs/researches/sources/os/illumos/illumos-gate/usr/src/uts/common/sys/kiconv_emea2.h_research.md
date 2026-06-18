# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/kiconv_emea2.h

## Role

`kiconv_emea2.h` is the CP720 companion table header for illumos kernel iconv EMEA support. It is separated from `kiconv_emea1.h` and contains the Arabic DOS code page 720 mapping pair used for CP720-to-UTF-8 and UTF-8-to-CP720 conversion.

The file comments state that only mappings guaranteeing exact one-to-one round-trip conversion are provided, for compatibility with previous CP720 conversions in storage products.

## Major Definitions

The header is protected by `_SYS_KICONV_EMEA2_H`, exposes C linkage for C++ consumers, includes `<sys/kiconv.h>`, and only declares table data under `_KERNEL`.

It defines:
- `static const kiconv_to_utf8_tbl_comp_t cp720_to_u8_tbl[128]`
- `static const kiconv_to_sb_tbl_comp_t u8_to_cp720_tbl[128]`

`cp720_to_u8_tbl` maps CP720 byte values `0x80` through `0xFF` to UTF-8 bytes, again by subtracting `0x80` from the input byte. `u8_to_cp720_tbl` maps packed UTF-8 values back to CP720 single-byte values and is sorted for binary search.

## Data Shape

The forward CP720 table has exactly 128 valid entries: 74 entries encode as two-byte UTF-8 sequences and 54 entries encode as three-byte UTF-8 sequences. Unlike several `kiconv_emea1.h` encodings, this table has no `{ 0xFE, 0xFE, 0xFE }` invalid placeholders.

The mappings include C1/control-compatible byte mappings, accented Latin characters, Arabic letters and marks, box-drawing/block characters, mathematical symbols, and non-breaking space. The first forward entry maps `0x80` to packed bytes `C2 80`; the last maps `0xFF` to `C2 A0`.

The reverse CP720 table has exactly 128 entries. A whole-table ordering check found no descending transitions and no duplicate packed UTF-8 keys. Its first entries cover packed C1/control-compatible UTF-8 keys such as `0x00C280`, and its final entries cover three-byte box/block characters such as `0xE296A0`.

## Runtime Use

The central `kiconv.c` code-list recognizes `cp720` and `720` as code id `33`, and the conversion list places code id `33` in the `kiconv_emea` module group. The table contract mirrors the common single-byte conversion machinery:
- ASCII input below `0x80` is copied directly.
- CP720 high-half bytes index this table by `byte - 0x80`.
- UTF-8 output length is derived from the first stored UTF-8 byte.
- Reverse conversion uses a packed UTF-8 key and binary search over the sorted reverse table.

Because this file keeps only exact round-trip mappings, changing either table can affect compatibility with stored data encoded under earlier CP720 behavior.

## Dependencies

This file depends on the same `sys/kiconv.h` component structures as `kiconv_emea1.h`: `kiconv_to_utf8_tbl_comp_t` for forward mappings and `kiconv_to_sb_tbl_comp_t` for reverse mappings.

Runtime UTF-8 validation and byte-length decisions come from shared kiconv UTF-8 tables outside this header. `usr/src/uts/common/sys/Makefile` lists `kiconv_emea2.h` as an exported kernel header.

## Maintenance Notes

The forward and reverse tables must stay bijective for the 128 CP720 high-half values if the documented exact round-trip behavior is to remain true. The forward table must stay 128 entries wide for direct indexing, and the reverse table must remain sorted by packed UTF-8 key for binary search.

Since CP720 is exposed as code id `33` in the EMEA conversion group, any attempt to merge this table into the larger 24-table file or renumber EMEA mappings needs a matching update to module open/convert code.
