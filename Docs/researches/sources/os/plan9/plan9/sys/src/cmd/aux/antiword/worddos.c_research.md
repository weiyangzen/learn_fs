# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/antiword/worddos.c

This file initializes Word for DOS documents.

Key behavior:
- Reads the 128-byte Word for DOS header.
- Verifies the DOS magic identifier and detected version.
- Rejects autosave/fast-saved DOS documents.
- Adds a single non-Unicode text block starting after the 128-byte header.
- Triggers property, tab-width, and notes extraction for version 0.

Important details:
- Text length is derived from the header’s file length field minus the header size.
- Property and notes extraction are called with no OLE PPS/depot data.

Filesystem relevance:
- Direct parsing of flat pre-OLE Word document files.
