# File Research: sources/os/plan9/plan9/sys/src/cmd/tcs/misc.h

## Purpose

`misc.h` defines multiple 256-entry single-byte character-set-to-Unicode tables used directly by `tcs.c`.

## Contents

Tables defined:

- `tabatari`: Atari ST character set, with ASCII identity in the lower half and accented Latin, Hebrew, Greek, and math symbols in the upper half.
- `tabebcdic`: EBCDIC to Unicode/ASCII-ish mapping with many `-1` invalid entries and comments for known substitutions.
- `tabmacroman`: Macintosh Standard Roman mapping.
- `tabnextstep`: NEXTSTEP encoding vector mapping, including combining marks and `0xFFFF` placeholders at the end.
- `tabps2`: IBM PS/2-style mapping, noted in `tcs.c` as aliased to IBM code page 850 for the active converter registry.
- `tabsf1`, `tabsf2`: Finnish/Swedish ISO-646 variants with many invalid upper-half entries.
- `tabtis620`: Thai TIS 620 mapping.
- `tabviet1`, `tabviet2`: Vietnamese VSCII variants.
- `tabviscii`: Vietnamese VISCII 1.1 mapping.

## Integration

`tcs.c` includes `misc.h` directly and registers most tables in `convert[]` as `Table` converters:

- `atari`, `ebcdic`, `macrom`, `next`, `sf1`, `sf2`, `tis-620`, `viet1`, `viet2`, `vscii`.
- `ps2` is present in this file, but `tcs.c` maps `ps2` to `tabcp850` from `ms.h`, not to `tabps2`.

For `Table` converters, `tcs.c` dispatches through `intable()`, which treats these arrays as byte-to-rune maps.

## Notes

This header defines storage, not just declarations. It is intended to be included once by `tcs.c`; including it from multiple translation units would create duplicate global definitions. `-1` entries are meaningful conversion failures.
