# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/zfilterx.c

## Purpose
Registers nonstandard extended filters: bounded Huffman, Burrows-Wheeler block sorting, byte translation, move-to-front, plus a code-table computation operator.

## Key Functions
- `bhc_setup()` validates bounded Huffman dictionaries and constructs count/value tables.
- `zBHCE()` and `zBHCD()` create bounded Huffman encode/decode filters.
- `zcomputecodes()` computes canonical Huffman code counts and values from an array of frequencies.
- `bwbs_setup()`, `zBWBSE()`, and `zBWBSD()` handle Burrows-Wheeler block sorting filters.
- `bt_setup()`, `zBTE()`, and `zBTD()` handle 256-byte translation tables.
- `zMTFE()` and `zMTFD()` create move-to-front filters.

## Important Behavior
- `Tables` for bounded Huffman must include code-length counts followed by values; the accumulated code space must fill exactly.
- `EncodeZeroRuns` is constrained by whether an end-of-data code is present.
- `.computecodes` replaces array entries in-place with computed table data.
- Byte translation requires an exact 256-byte string.

## Research Notes
These filters are Ghostscript extensions rather than core PostScript filter names, but they use the same `filter_read`/`filter_write` infrastructure.
