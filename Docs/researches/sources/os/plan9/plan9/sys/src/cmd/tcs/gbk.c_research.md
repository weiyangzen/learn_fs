# File Research: sources/os/plan9/plan9/sys/src/cmd/tcs/gbk.c

This file is the static GBK-to-Unicode mapping payload for Plan 9's `tcs` converter. It contains no conversion control flow beyond including `gbk.h` and defining `long tabgbk[]`.

Key contents:
- `tabgbk[]` has 32,016 entries, exactly matching `GBKMAX - GBKMIN` for the byte-pair interval `[0x8140, 0xFE50)`.
- Each table index corresponds to a packed GBK two-byte code minus `GBKMIN`.
- Non-negative entries are Unicode/Plan 9 rune values; `-1` marks invalid, unassigned, or unsupported GBK byte-pair slots.
- The table includes CJK ideographs, punctuation, fullwidth forms, kana, Greek, Cyrillic, box-drawing, compatibility ideographs, radicals, and many extended GBK assignments.

Important details:
- Actual GBK input/output logic lives in `conv_gbk.c`; that code indexes `tabgbk[c - GBKMIN]` for input and builds a reverse `tab[]` map from `tabgbk[]` for output.
- Because output reverse mapping is built by assigning `tab[tabgbk[i-GBKMIN]] = i`, duplicate Unicode values in this data would resolve to the later GBK code point.
- The table is dense over the numeric GBK range, not compacted by valid lead/trail-byte classes, so invalid holes remain explicit `-1` values.
- The source is data-heavy and appears generated or imported from a character-set mapping source.

Filesystem relevance:
- Indirect: supports text transcoding for files and streams handled by `tcs`; it is not filesystem implementation code.
