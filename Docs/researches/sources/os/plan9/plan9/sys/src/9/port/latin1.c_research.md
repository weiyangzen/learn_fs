# File Research: sources/os/plan9/plan9/sys/src/9/port/latin1.c

Purpose: Latin-1/compose-key style rune lookup helper.

Key logic:
- Builds `latintab[]` by including `latin1.h`.
- `unicode` parses hex digits after `X`/`x` prefixes into a rune value.
- `latin1` maps a sequence of 2 or 3 runes to a composed rune, returns `-1` on invalid sequence, or a negative required-length value when more input is needed.
- Handles `X` as fixed 4-hex-digit input and `x` as `UTFmax*2` hex digits.

Dependencies and integration:
- Uses `Rune` and `UTFmax` from port library definitions.
- Used by keyboard/console compose logic.

Risks and notes:
- Relies on ordering and prefix assumptions documented at the top of the file.
