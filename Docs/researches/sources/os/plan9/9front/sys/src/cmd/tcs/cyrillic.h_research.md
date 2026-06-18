# File Research: sources/os/plan9/9front/sys/src/cmd/tcs/cyrillic.h

Defines five 256-entry single-byte Cyrillic mapping tables.

Key points:
- Defines `long tabucode[256]`, `tabkoi8[256]`, `tab866[256]`, `tabav[256]`, and `tabov[256]`.
- All tables map ASCII `0x00-0x7f` to identical Unicode code points.
- Unassigned or unsupported byte positions are represented with `-1`.
- `tabucode` maps a compact Russian U-code range to Cyrillic capitals/lowercase beginning around byte `0xB0`.
- `tabkoi8` maps KOI-8/KOI8-R-style byte positions to Cyrillic, including Ukrainian/Belarusian additions such as `0x0404`, `0x0406`, `0x0407`, `0x0490`, and lowercase counterparts.
- `tab866` maps DOS code page 866 Cyrillic ranges, with uppercase and lowercase split across high-byte regions and `0x0401/0x0451` near the end.
- `tabav` and `tabov` cover Alternativnyj Variant and Osnovnoj Variant layouts, including Cyrillic plus symbols such as combining acute/grave, arrows, division, plus-minus, numero, and currency sign.

Dependencies and interactions:
- Included directly by `tcs.c`.
- `tcs.c` registers these arrays as table-backed charsets: `ucode`, `koi8`, `koi8-r`, `866`, `av`, and `ov`.

Research relevance:
- Static single-byte charset mapping data for Cyrillic encodings.
