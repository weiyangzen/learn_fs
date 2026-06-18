# File Research: sources/teaching/xv6-public/kbd.c

PC keyboard interrupt input decoder.

Key behavior:
- Reads keyboard controller status/data ports.
- Tracks modifier, toggle, and E0 escape state.
- Maps scan codes through `normalmap`, `shiftmap`, or `ctlmap`.
- Applies Caps Lock case toggling.
- `kbdintr` passes decoded characters to `consoleintr`.

Limitations:
- Supports the simple PC keyboard scan-code path used by xv6; no advanced keyboard protocol handling.
