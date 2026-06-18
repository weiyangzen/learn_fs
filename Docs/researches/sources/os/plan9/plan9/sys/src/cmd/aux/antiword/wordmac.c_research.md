# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/antiword/wordmac.c

This file initializes old Macintosh Word 4/5 documents.

Key behavior:
- Reads a 256-byte header and verifies the Mac Word magic value.
- Rejects fast-saved Mac documents.
- Reads big-endian text start/end offsets and creates one non-Unicode text block.
- Invokes property extraction and default tab-width setup for Word 4/5.

Important details:
- Character positions are initialized to the same values as file offsets.
- Word 4/5 property extraction is effectively sparse in `properties.c`.

Filesystem relevance:
- Direct parsing of flat pre-OLE Macintosh Word files.
