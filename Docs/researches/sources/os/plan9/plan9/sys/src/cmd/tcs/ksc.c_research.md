# File Research: sources/os/plan9/plan9/sys/src/cmd/tcs/ksc.c

## Purpose

`ksc.c` is a generated/static mapping table for Plan 9 `tcs` Korean character conversion. It maps KS C 5601 / KSC 5601 two-byte code positions to Unicode rune values.

## Contents

- Includes `ksc.h`.
- Defines `long tabksc5601[]`.
- Defines `int ksc5601max = sizeof(tabksc5601)/sizeof(tabksc5601[0])-1`.

The table comment explains the indexing rule:

- KSC uses 94x94 code positions.
- Each byte’s 7-bit portion is offset by `33` (`0x21`), not `32`.
- Lookup index is `(n - 33) * 94 + (m - 33)` for KSC bytes `(n, m)`.
- `-1` entries mean undefined/unmapped code positions.
- The final `0` is a sentinel/end marker, excluded from `ksc5601max`.

## Integration

`conv_ksc.c` uses this file through `ksc.h`:

- Input path computes `n = ((lastc & 0x7f) - 33) * 94 + (c & 0x7f) - 33`.
- It rejects indexes `>= ksc5601max` or table values `< 0`.
- Output path builds the reverse global `tab[NRUNE]` from `tabksc5601`.

The table supports `euc-k`, `euc-kr`, and `ks_c_5601-1987` converter entries registered in `tcs.c`.

## Notes

This file contains no executable conversion logic beyond `ksc5601max`; its correctness depends entirely on table order, sentinel placement, and the `conv_ksc.c` indexing formula. Any edit to table length or ordering can silently corrupt Korean conversion.
