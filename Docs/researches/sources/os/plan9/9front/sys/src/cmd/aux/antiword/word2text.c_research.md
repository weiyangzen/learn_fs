# File Research: sources/os/plan9/9front/sys/src/cmd/aux/antiword/word2text.c

Main Word-to-output conversion state machine.

Key responsibilities:
- Initializes a Word document, parses metadata/properties, prepares headers/footers and footnotes, and emits output prologue.
- Reads translated characters from text, footnote, endnote, textbox, and header textbox lists.
- Tracks current section, row/table state, style transitions, font transitions, list state, hidden/deleted text flags, and current image reference.
- Builds linked `output_type` fragments with font/style/width metadata.
- Handles paragraph breaks, page/column breaks, hard returns, tabs, table separators, footnotes/endnotes, images, lists, indentation, and wrapping.
- Frees document-wide parsed structures at the end.

Important behavior:
- `ulGetChar()` is the character ingestion point: it advances text lists, detects row/style/font starts, skips embedded regions, translates Word characters, records pictures, and prepares next-style/font defaults at paragraph ends.
- `bWordDecryptor()` wraps lines, switches output lists after EOF, renders table rows specially, and uses `[pic]` fallback when image translation fails.
- Text-list EOF flows through main text, footnotes, endnotes, text boxes, and header text boxes.
- XML output suppresses some text-only behavior and handles footnote text differently.
- Hidden and revision-deleted text are filtered based on options.

Dependencies:
- Document initialization, property/style/font/row/list/section/picture/note stores, character translation, image translation, output backends, font metrics.

Notable risks:
- This file is highly stateful; correctness depends on parser lists being ordered by file offset/sequence.
- Table rendering relies on both row-list offsets and property-modifier row detection.
