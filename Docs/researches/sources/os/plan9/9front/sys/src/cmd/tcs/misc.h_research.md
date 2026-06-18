# File Research: sources/os/plan9/9front/sys/src/cmd/tcs/misc.h

## Purpose
Defines multiple 256-entry single-byte character-set mapping tables used directly by the generic `tcs` table converter.

## Key Elements
Provides these `long[256]` tables:
- `tabatari`: ATARI-ST character set, ASCII identity in low half plus accented Latin, Hebrew, Greek, and symbols.
- `tabebcdic`: EBCDIC mapping with many `-1` unmapped slots and comments about compatibility substitutions.
- `tabmacroman`: Macintosh Standard Roman mapping, including ligatures and private-use-style Apple symbol `0xf7ff`.
- `tabnextstep`: NEXTSTEP encoding vector, including combining marks and two final `0xffff` entries.
- `tabps2`: IBM PS/2-style mapping with Latin, box drawing, and symbols.
- `tabsf1`, `tabsf2`: Finnish/Swedish ISO-646 variants with high-half unmapped entries.
- `tabtis620`: Thai TIS-620 mapping with unmapped gaps.
- `tabviet1`, `tabviet2`: Vietnamese VSCII variants with combining marks and precomposed Vietnamese letters.
- `tabviscii`: Vietnamese VISCII 1.1 mapping.

All tables were scanned as full 256-entry arrays after comment removal. Notable unmapped counts: `tabebcdic` 128, `tabsf1` 112, `tabsf2` 112, `tabtis620` 41, `tabviet1` 17, `tabviet2` 32. `tabatari`, `tabmacroman`, `tabnextstep`, `tabps2`, and `tabviscii` have no `-1` entries.

## Dependencies
These tables are registered in `tcs.c` as `Table` converters under names including `atari`, `ebcdic`, `macrom`, `next`, `sf1`, `sf2`, `tis-620`, `viet1`, `viet2`, and `vscii`.

## Behavior/Risks
Despite the `.h` suffix, this file defines storage, not just declarations. It must be included in exactly the intended compilation unit or duplicate definitions would result.

The generic table converter interprets `-1` as unmappable. Tables with compatibility substitutions, `0xffff`, combining marks, or private-use values may not round-trip cleanly through other encodings. Since these are direct byte-indexed tables, each array must remain exactly 256 logical entries.

## Verification
Read completely: 304 lines, 19274 bytes. SHA-256: `e2730f899d627a2bf27ceb510b2be52af45bef1dc26dffdf1899fb9e904f68ed`.
