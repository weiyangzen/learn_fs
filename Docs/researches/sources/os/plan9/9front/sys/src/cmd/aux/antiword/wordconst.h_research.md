# File Research: sources/os/plan9/9front/sys/src/cmd/aux/antiword/wordconst.h

Shared constants and macros for Word binary interpretation and rendering.

Key contents:
- Boolean definitions for non-C99 portability.
- OLE/Word block sizes: header, big block, small block, PPS entry, and BBD threshold.
- Table, tab, font size, font style, font color, list type, alignment, and border constants.
- Invalid/sentinel values for character positions, file offsets, style IDs, block chains, and property modifiers.
- Little-endian and big-endian byte extraction macros.
- Font-style and table-border predicate macros.
- Unit conversion macros for twips, millipoints, draw units, points, and character cells.
- Word control-character constants and pseudo-character values for notes.
- Unicode constants used by character translation and output fallback.

Research relevance:
- This is the low-level compatibility contract used across the Antiword parser and renderers.
