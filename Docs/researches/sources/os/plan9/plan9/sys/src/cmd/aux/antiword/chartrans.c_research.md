# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/antiword/chartrans.c

This file translates Word character codes and Unicode values into Antiword’s selected local output encoding.

Key behavior:
- Contains codepage tables for DOS CP850, Windows CP1250/1251/1252, MacRoman, and Microsoft private-use symbols.
- Reads external character mapping tables, stores local-byte-to-Unicode mappings, and sorts them for binary search.
- Returns local bullet and non-breaking-space representations.
- Converts Word control/special characters into internal markers or ignores non-printing controls.
- Handles PS/PDF-specific Latin-1 substitutions for typography.
- Falls back from many Unicode punctuation, spaces, arrows, boxes, and symbols to simple ASCII approximations.
- Provides locale-independent uppercase conversion for ASCII and common Latin-1 characters.

Important details:
- UTF-8 output bypasses local table conversion and returns Unicode code points.
- Word note markers are resolved through `eGetNotetype()` based on file offset.
- Unmappable characters usually become `?`, except some layout/control marks are ignored.

Filesystem relevance:
- Indirect: consumes character data extracted from Word file streams and support mapping files.
