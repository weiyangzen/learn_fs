# File Research: sources/os/plan9/plan9/sys/src/cmd/tcs/kuten212.c

## Purpose

`kuten212.c` defines a JIS X 0212-style supplementary kuten-to-Unicode table.

## Contents

- Includes `kuten212.h`.
- Defines `long tabkuten212[KUTEN212MAX]`.
- Uses `-1` for unassigned positions.
- Contains large ranges of symbols, accented Latin/Greek/Cyrillic characters, and many CJK ideographs.

The layout mirrors the other kuten table style: direct numeric indexing into a fixed-length array, with many sparse holes.

## Integration

The local cross-reference pass found `kuten212.h` and `kuten212.c` in the tree, but no active converter in this `tcs` directory references `tabkuten212`. In the current source snapshot, it appears to be a prepared/static mapping asset rather than wired into the converter registry in `tcs.c`.

## Notes

Because no active call site was found, the primary risks are dead-code drift and table-size mismatch if a future converter starts using it. If activated, callers should follow the same pattern as `tabkuten208`: bounds check against `KUTEN212MAX`, treat `-1` as unmapped, and preserve table indexing semantics.
