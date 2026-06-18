# File Research: sources/teaching/xv6-public/kbd.h

Keyboard constants and scan-code maps.

Contents:
- Keyboard controller ports and status bits.
- Modifier/toggle flags and special key constants.
- `C(x)` control-character macro.
- `shiftcode`, `togglecode`, `normalmap`, `shiftmap`, and `ctlmap` arrays.

Role:
- Used exclusively by `kbd.c` to translate raw keyboard bytes into console input characters and special key values.
