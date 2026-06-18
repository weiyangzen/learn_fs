# File Research: sources/os/plan9/plan9/sys/src/cmd/tcs/kuten208.c

## Purpose

`kuten208.c` defines the JIS X 0208 Unicode mapping table used by Plan 9 `tcs` Japanese encoders and decoders.

## Contents

- Includes `kuten208.h`.
- Defines `long tabkuten208[KUTEN208MAX]`.
- Uses `-1` for invalid or unassigned kuten positions.
- Starts with padding entries so callers can index directly by the encoded kuten number used in `conv_jis.c`.

The table includes punctuation, kana, Greek, Cyrillic, box drawing characters, common CJK ideographs, and extended rows represented as Unicode code points.

## Integration

`conv_jis.c` includes `kuten208.h` and uses `tabkuten208` for several Japanese input paths:

- ISO-2022-JP / `jis-kanji`.
- Shift-JIS / `ms-kanji`.
- EUC-JX / `ujis`.
- Guessing mode `jis`.

Typical lookup flow:

- Convert input bytes into a kuten208 integer.
- Check `n >= KUTEN208MAX` or `tabkuten208[n] == -1`.
- Emit `BADMAP` on unmapped input unless `clean` is enabled.
- For output, `tab_init()` builds a reverse map from rune to kuten index.

`font/kmap.c` also reads `tabkuten208` to create font mapping data.

## Notes

This is a core data dependency for Japanese conversion. The fixed macro size from `kuten208.h` is part of the ABI between the table and callers. Table order and padding are semantically significant.
