# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/zfilterx.c

## Purpose
Registers nonstandard extended filters: bounded Huffman, Burrows-Wheeler block sorting, byte translation, move-to-front, plus a code-table computation operator.

## Key Functions
- `bhc_setup()` validates bounded Huffman dictionaries and constructs count/value tables.
- `zBHCE()` and `zBHCD()` create bounded Huffman encode/decode filters.
- `zcomputecodes()` computes canonical Huffman code counts and values from frequencies.
- `zBWBSE()` / `zBWBSD()` handle Burrows-Wheeler block sorting filters.
- `zBTE()` / `zBTD()` handle 256-byte translation tables.
- `zMTFE()` / `zMTFD()` create move-to-front filters.

## Important Behavior
- Bounded Huffman tables must fill the code space exactly.
- `.computecodes` replaces array entries in-place.
- Byte translation requires an exact 256-byte string.

## Research Notes
Ghostscript extension filters using the same `filter_read`/`filter_write` infrastructure.
