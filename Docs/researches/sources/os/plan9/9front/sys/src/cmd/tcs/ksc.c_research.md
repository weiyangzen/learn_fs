# File Research: sources/os/plan9/9front/sys/src/cmd/tcs/ksc.c

## Purpose
Defines the KS C 5601 to Unicode mapping table used by the Korean EUC converter.

## Key Elements
Includes `ksc.h` and defines `long tabksc5601[]`, a compressed mapping table for the 94x94 KS C 5601 codeset. The file comments document the index formula: for KS C 5601 code point `(n, m)`, lookup index is `(n - 33) * 94 + (m - 33)`.

The table starts with punctuation/symbol mappings such as `0x3000`, includes Hangul and Hanja ranges, uses `-1` for unmapped slots, and ends with a terminal `0` sentinel. `int ksc5601max = sizeof(tabksc5601)/sizeof(tabksc5601[0])-1` excludes that sentinel from converter iteration and bounds checks.

## Dependencies
Declared in `ksc.h` and consumed by `conv_ksc.c`. `ukscproc` indexes `tabksc5601` for EUC-K input and treats `< 0` entries as unknown mappings. `uksc_out` builds the reverse `tab[]` lookup by scanning `0..ksc5601max-1`.

## Behavior/Risks
This file is pure table data with no executable control flow besides the global `ksc5601max` initializer. Converter correctness depends on the table order exactly matching the `(row,column)` indexing formula. A misplaced row changes both input decoding and reverse output encoding.

Unmapped slots are represented as `-1`; `conv_ksc.c` increments conversion errors and emits `BADMAP`/`BYTEBADMAP` unless clean mode suppresses output. The terminal zero is not part of the logical table because `ksc5601max` subtracts one.

## Verification
Read completely: 988 lines, 72413 bytes. SHA-256: `26cfb392fdd22a5a33c8e70d196628d0a2385812dcd60edfce74999fdcc6773c`.
