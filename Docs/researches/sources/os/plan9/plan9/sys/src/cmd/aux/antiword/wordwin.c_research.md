# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/antiword/wordwin.c

This file initializes WinWord 1/2 documents.

Key behavior:
- Reads a 384-byte header and verifies WinWord 1.x or 2.0 magic.
- Rejects fast-saved and encrypted documents.
- Builds one text block covering main text plus footnotes, headers/footers, macros, and annotations.
- Splits the block list into logical text sublists.
- Builds a coarse data block for images when image output is enabled.
- Invokes property, tab-width, and notes extraction.

Important details:
- Data block discovery uses the range between end-of-text and character-info start as an image-containing region.
- Text-only, formatted-text, XML, and no-image modes skip data block setup.

Filesystem relevance:
- Direct parsing of flat pre-OLE Windows Word files.
