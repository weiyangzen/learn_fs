# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/antiword/doclist.c

This file stores the single document-information record used by Antiword.

Key behavior:
- Creates and destroys a one-record “document info list”.
- Returns the default tab width, falling back to half an inch when unavailable or zero.
- Returns the document header/footer specification byte from the stored document properties.

Important details:
- There is no real linked list; `pAnchor` points to a static `document_block_type`.
- Tab width is converted from twips to millipoints.

Filesystem relevance:
- Indirect: holds parsed document metadata after it is read from Word file streams.
