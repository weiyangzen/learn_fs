# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/antiword/blocklist.c

This file builds, splits, reads, and maps Antiword’s logical Word text block lists.

Key behavior:
- Maintains separate linked lists for main text, footnotes, headers/footers, macros, annotations, endnotes, text boxes, and header text boxes.
- Adds contiguous text blocks and merges adjacent compatible blocks.
- Splits the initially collected text stream into per-region lists using document character lengths.
- Removes empty text-box lists by reading their bytes and checking for whitespace/control-only content.
- Provides streaming character readers that handle byte and Unicode text blocks.
- Converts logical character positions to physical file offsets, header/footer offsets to character positions, and text file offsets to sequence numbers.

Important details:
- `readinfo_type` caches `BIG_BLOCK_SIZE` chunks and keeps independent cursors for general text, headers/footers, and footnotes.
- Unicode blocks consume two bytes per character.
- Some lengths are in characters while block lengths are stored in bytes; split logic accounts for this.
- Optional extension pads intermediate block lengths to big-block boundaries for certain file layouts.

Filesystem relevance:
- Direct document-storage mapping: translates Word logical text ranges into physical offsets inside compound-file block chains.
