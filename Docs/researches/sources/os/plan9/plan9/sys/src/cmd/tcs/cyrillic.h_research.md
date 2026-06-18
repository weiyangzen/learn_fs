# File Research: sources/os/plan9/plan9/sys/src/cmd/tcs/cyrillic.h

Static Cyrillic-related byte-to-rune mapping tables.

Tables:
- `tabucode`: main Cyrillic block in upper half.
- `tabkoi8`: KOI8 Cyrillic layout.
- `tab866`: DOS code page 866 subset with Cyrillic.
- `tabav` and `tabov`: alternative Cyrillic/typographic mappings including arrows, accents, division, plus-minus, numero sign, and currency sign.

Conventions:
- `long[256]` arrays.
- ASCII/control positions are identity mappings.
- Undefined entries are `-1`.

Role:
- Used by `tcs` single-byte conversion definitions outside this subset.
