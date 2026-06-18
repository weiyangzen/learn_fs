# File Research: sources/os/plan9/9front/sys/src/cmd/aux/antiword/notes.c

Footnote/endnote table reader for distinguishing note references and preparing footnote body text.

Key responsibilities:
- Maintains global footnote-reference, endnote-reference, and footnote-text lists.
- Parses Word for DOS, WinWord 1/2, Word 6/7, and Word 8+ note PLCF structures from version-specific FIB offsets.
- Selects direct file reads for older flat files and big/small block depot reads for compound-file table streams.
- Converts note character positions to file offsets for later reference classification.
- Prepares footnote text lazily through `szFootnoteDecryptor()`.
- Exposes cleanup, note type lookup, and indexed footnote text retrieval.

Dependencies:
- Uses Antiword block depot readers, character-position/file-offset conversion, PPS table-stream metadata, and `footnote_block_type`.

Notable risks:
- State is global and must be reset with `vDestroyNotesInfoLists()` between documents.
- Endnote references are tracked, but only footnote text bodies are stored here.
- `szGetFootnootText()` contains a spelling error in the public symbol name, likely preserved for internal callers.
