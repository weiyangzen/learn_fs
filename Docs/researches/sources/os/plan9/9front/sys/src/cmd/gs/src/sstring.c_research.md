# File Research: sources/os/plan9/9front/sys/src/cmd/gs/src/sstring.c

Implements ASCII hex and PostScript string stream filters plus shared hex decoding.

Key points:
- `ASCIIHexEncode` writes uppercase hex pairs, inserts newlines after 32 bytes, and optionally emits `>` at EOD.
- `ASCIIHexDecode` uses `s_hex_process`, handles odd final hex digits by padding the low nibble, scans ahead for `>`, and returns EOFC at EOD.
- `PSStringEncode` escapes nonprintable bytes, named escapes, octal escapes, parentheses, and backslash, appending `)` at finalization.
- `PSStringDecode` handles backslash escapes, octal escapes, escaped newlines, nested parentheses via depth tracking, CR/LF normalization, and Level 1 `from_string` behavior.
- `s_hex_process` converts hex text to bytes with selectable syntax: ignore all whitespace, ignore leading whitespace only, or ignore garbage.
- All routines follow Ghostscript's offset-by-one stream cursor convention.

Dependencies and interactions:
- State definitions are in `sstring.h`.
- `s_hex_process` is reused by eexec decoding and ASCIIHexDecode.

Research relevance:
- Core textual string/hex filter utilities for PostScript scanning and output.
