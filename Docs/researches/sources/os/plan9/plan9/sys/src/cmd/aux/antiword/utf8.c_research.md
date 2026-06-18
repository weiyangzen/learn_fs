# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/antiword/utf8.c

This file implements UTF-8 width and locale helpers.

Key behavior:
- Contains a table of combining/zero-width Unicode intervals.
- Converts UTF-8 byte sequences to UCS values.
- Computes display column width for UTF-8 strings using a Kuhn-derived `wcwidth` approach.
- Reports the byte length of a UTF-8 character.
- Detects whether the normalized locale codeset is UTF-8.

Important details:
- Invalid or truncated UTF-8 is not strongly validated; missing continuation bytes contribute zeroed payload bits.
- East Asian wide/fullwidth ranges count as width 2, combining/control handling follows the local table.

Filesystem relevance:
- None directly; supports correct text layout of decoded document content.
