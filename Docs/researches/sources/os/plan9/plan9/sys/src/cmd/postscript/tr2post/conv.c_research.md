# File Research: sources/os/plan9/plan9/sys/src/cmd/postscript/tr2post/conv.c

Purpose: Main troff device-independent input interpreter for `tr2post`.

Key behavior:
- Reads one command rune at a time and dispatches troff output commands.
- Handles point size, font position, literal rune, special character, absolute/relative motion, compact two-digit motion plus character, page starts, line records, word spaces, drawing commands, and device-control commands.
- Ignores numeric character command `N` after parsing its number.
- Tracks `inputlineno`.
- Calls `endpage` at EOF.

Dependencies and integration:
- Calls `settrfont`, `runeout`, `specialout`, `hgoto`, `vgoto`, `hmot`, `vmot`, `draw`, `devcntl`, `startpage`, and `endpage`.

Risks and notes:
- Unknown troff commands are warnings, not fatal.
- Numeric glyph command `N` is effectively unimplemented.
- Uses `Brdline` to discard trailing data for comments and line records.
