# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/kiconv_latin1.h

## Role

Kernel-only single-byte Western encoding conversion tables for illumos `kiconv`. It supports CP1252, ISO 8859-1, ISO 8859-15, and CP850 in both directions against UTF-8.

## Structure

- Lines 1-66: CDDL header, Sun copyright, Unicode data permission notice, and modification note.
- Lines 68-77: include guard, C++ linkage wrapper, include of `<sys/kiconv.h>`, then `_KERNEL` gating.
- Lines 79-88: comments describe `to_u8_tbl`; indices are source byte minus 0x80 and each entry stores up to three UTF-8 bytes. Invalid entries have a first byte that maps to an invalid size in the shared UTF-8 byte-count table.
- Lines 90-618: `static const kiconv_to_utf8_tbl_comp_t to_u8_tbl[4][128]`.
- Lines 91-221: CP1252 to UTF-8 entries for 0x80-0xff. Undefined CP1252 C1 slots 0x81, 0x8d, 0x8f, 0x90, and 0x9d are encoded as `{ 0xFE, 0xFE, 0xFE }`.
- Lines 222-352: ISO 8859-1 to UTF-8 entries for 0x80-0xff, including C1 controls as C2 80 through C2 9F and Latin-1 supplement characters.
- Lines 353-483: ISO 8859-15 to UTF-8 entries. It differs from ISO 8859-1 at standard Latin-9 replacement positions such as 0xa4 euro, 0xa6/0xa8 S caron pairs, 0xb4/0xb8 Z caron pairs, and 0xbc/0xbd OE pairs.
- Lines 484-618: CP850 to UTF-8 entries, including accented Latin letters, box-drawing characters, block elements, and DOS code page symbols.
- Lines 620-627: comments describe `to_sb_tbl`; each entry stores a packed 24-bit UTF-8 byte sequence and an 8-bit single-byte result, sorted by UTF-8 key for binary search.
- Lines 628-1141: `static const kiconv_to_sb_tbl_comp_t to_sb_tbl[4][128]`.
- Lines 629-758: UTF-8 to CP1252. It includes sorted mappings for Latin-1 supplement, CP1252 punctuation, euro, trademark, and padding sentinel entries `{ 0xFFFFFF, 0x00 }` for undefined byte positions.
- Lines 759-889: UTF-8 to ISO 8859-1. This maps C1 controls and Latin-1 supplement UTF-8 forms back to bytes 0x80-0xff.
- Lines 890-1018: UTF-8 to ISO 8859-15. The table omits replaced Latin-1 characters that ISO 8859-15 does not encode and includes euro/OE/caron mappings.
- Lines 1019-1141: UTF-8 to CP850. The table covers Latin, box-drawing, and block symbols used by CP850.
- Lines 1143-1149: closes `_KERNEL`, C++ wrapper, and guard.

## Dependencies And Consumers

- Depends on `kiconv_to_utf8_tbl_comp_t` and `kiconv_to_sb_tbl_comp_t` from `kiconv.h`.
- The forward table is indexed by conversion id and source byte offset. In `usr/src/uts/common/os/kiconv.c`, conversion paths use `to_u8_tbl[id][k]` and `u8_number_of_bytes[first_byte]` to decide how many bytes to emit.
- Reverse conversion paths binary-search `to_sb_tbl[id]` by packed UTF-8 value. The comments and table ordering are part of that contract.
- Tables are `static const` in a header, so included translation units receive private read-only copies.

## Important Behaviors

- Only bytes 0x80-0xff are represented. ASCII bytes 0x00-0x7f are handled directly by converter logic, not by these tables.
- CP1252 invalid bytes use `0xfe` sentinel bytes in `to_u8_tbl`, while reverse CP1252 uses `0xffffff` sentinels at the end of the sorted table. Consumers must preserve this convention.
- ISO 8859-1 is treated as a full 0x80-0xff byte-to-Unicode mapping, including C1 controls, rather than rejecting the 0x80-0x9f range.
- The packed UTF-8 keys are byte sequences, not Unicode scalar values. For example, euro is represented as `0xe282ac`.

## Risks And Gotchas

- `to_sb_tbl` must remain sorted by packed UTF-8 key for binary search. A single out-of-order edit can make valid characters unconvertible.
- The two table families encode invalid/unassigned entries differently. Treating `0xfe` and `0xffffff` as equivalent without considering direction would be wrong.
- The table id ordering is implicit: CP1252, ISO 8859-1, ISO 8859-15, CP850. Callers must use matching ids.
- Because arrays are header-local, including this file from multiple C files duplicates approximately 34 KB of table source data in object form.

## Research Notes

Read completely: 1149 lines, 33868 bytes.
