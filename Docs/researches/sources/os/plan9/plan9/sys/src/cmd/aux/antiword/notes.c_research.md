# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/antiword/notes.c

## Summary
`notes.c` builds and owns Antiword’s footnote/endnote metadata tables. It maps note reference positions to footnote/endnote types and prepares extracted footnote text for later output.

## Main Responsibilities
- Maintains global arrays for footnote reference offsets, endnote reference offsets, and footnote text records.
- Parses note metadata for Word for DOS, WinWord 1/2, Word 6/7, and Word 8 formats.
- Uses direct file reads for older flat formats and `bReadBuffer()` over Big/Small Block Depots for compound-document formats.
- Converts character positions to file offsets through `ulCharPos2FileOffset()`.
- Calls `szFootnoteDecryptor()` to materialize useful footnote text after note ranges are known.
- Exposes `eGetNotetype()` and `szGetFootnootText()` for downstream text processing.

## Key Dependencies
Depends on `antiword.h`, OLE block depot readers, FIB offset conventions, memory wrappers, and global character-position mapping functions.

## Filesystem Relevance
Reads structured regions from Word document files and compound streams but does not implement filesystem behavior.

## Notes
The implementation is version-specific and offset-table driven. Endnotes are absent for Word for DOS and WinWord 1/2 paths.
