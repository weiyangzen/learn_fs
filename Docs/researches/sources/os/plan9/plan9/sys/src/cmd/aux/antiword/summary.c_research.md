# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/antiword/summary.c

This file extracts document summary metadata and language information.

Key behavior:
- Stores title, subject, author, creation time, last-save time, application name, manager, company, and language ID.
- Parses DOS date strings, Word DTTM-derived values, and OLE FILETIME values.
- Reads OLE SummaryInformation and DocumentSummaryInformation streams through big/small block depots.
- Handles Word for DOS, WinWord 1/2, Word 6/7, and Word 8 summary sources.
- Provides getters for metadata strings, PDF-style dates, and locale-like language tags.

Important details:
- OLE property sections are validated for little-endian byte order and expected section count.
- LPSTR values are trimmed at both ends.
- Language ID handling includes many specific locale exceptions before applying a general low-byte language mapping.

Filesystem relevance:
- Directly parses OLE property streams embedded in the document container.
