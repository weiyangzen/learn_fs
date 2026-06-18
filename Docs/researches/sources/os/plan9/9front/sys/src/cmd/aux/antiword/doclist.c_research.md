# File Research: sources/os/plan9/9front/sys/src/cmd/aux/antiword/doclist.c

Small Antiword holder for document-level metadata.

Important behavior:
- Stores a single `document_block_type` in static storage; there is no real list despite the filename.
- `vCreateDocumentInfoList()` copies document info and sets the static anchor.
- `vDestroyDocumentInfoList()` clears the anchor.
- `lGetDefaultTabWidth()` returns document default tab width converted from twips to millipoints, falling back to half an inch.
- `ucGetDopHdrFtrSpecification()` returns header/footer specification bits.

Filesystem relevance:
- Supplies layout metadata derived from parsed document streams to output generators.
