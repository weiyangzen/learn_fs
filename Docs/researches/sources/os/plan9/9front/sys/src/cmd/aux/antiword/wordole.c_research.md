# File Research: sources/os/plan9/9front/sys/src/cmd/aux/antiword/wordole.c

OLE compound-document reader and Word 6+ initializer.

Key responsibilities:
- Reads big block depot and small block depot chains.
- Parses Property Set Storage directory entries and computes tree levels.
- Locates required Word streams: `WordDocument`, `Data`, `0Table`, `1Table`, SummaryInformation, and DocumentSummaryInformation.
- Rejects OLE files without Word streams and reports Excel workbooks specially.
- Reads the WordDocument FIB header and determines Word version.
- Chooses active table stream based on FIB flags.
- Builds text/data block lists, property lists, tab width, notes, and summary metadata for Word 6/7/8.

Important behavior:
- PPS tree recursion is capped to avoid infinite loops.
- Word 8 text uses `bGet8DocumentText()`; Word 6/7 fast-save paths use Word 6 helpers.
- Image data comes from the text stream for Word 6/7 and the `Data` stream for Word 8.
- All depot and small-block resources are freed through a shared cleanup macro.

Dependencies:
- Block readers, small block list builder, PPS stream structs, version-specific text/property/data parsers.

Notable risks:
- OLE chain and PPS validation is partial; corrupted depots can still hit fatal errors.
- Files with too-small WordDocument streams are rejected.
