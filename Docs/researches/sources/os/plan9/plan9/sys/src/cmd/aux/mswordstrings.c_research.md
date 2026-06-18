# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/mswordstrings.c

This file extracts rough plain text from a Microsoft Word `WordDocument` stream.

Key behavior:
- Defines and reads an auto-generated subset of the Word FIB header.
- Seeks from `fcMin` to `fcMac`.
- Emits text bytes while translating common Word control characters to newlines, tabs, field markers, or placeholder strings.
- Prints placeholders for pictures, footnotes, animation, line numbers, drawn objects, and date/time fields.

Important details:
- Intended usage references `/mnt/doc/WordDocument`, implying use after mounting/extracting an OLE document.
- Contains comments noting incomplete handling of mixed zero-padded text and special characters.
- Does not parse full Word piece tables or formatting.

Filesystem relevance:
- Indirect document stream extractor; consumes a file from a mounted document namespace.
