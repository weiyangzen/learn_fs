# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/antiword/wordole.c

This file parses OLE Compound File storage for Word 6 and later documents.

Key behavior:
- Reads Big Block Depot, Small Block Depot, root directory chain, and property set storage entries.
- Finds `WordDocument`, `Data`, `0Table`, `1Table`, `SummaryInformation`, and `DocumentSummaryInformation` streams.
- Chooses the active table stream from the Word header status bit.
- Reads the WordDocument FIB/header and initializes text, data, properties, tabs, and notes.
- Handles Word 6/7 and Word 8 text/data block discovery differently.

Important details:
- PPS entries are converted from UTF-16-ish names to narrow strings and assigned tree levels with recursion limits to avoid loops.
- Files without a WordDocument stream are distinguished from Excel workbooks for diagnostics.
- Small streams use the small-block depot; large streams use the big-block depot.
- The initializer rejects encrypted documents and unsupported pre-Word-6 OLE content.

Filesystem relevance:
- Direct and central: implements OLE compound-file stream traversal and substream discovery.
