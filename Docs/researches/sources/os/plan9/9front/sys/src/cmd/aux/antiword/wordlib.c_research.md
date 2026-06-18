# File Research: sources/os/plan9/9front/sys/src/cmd/aux/antiword/wordlib.c

Top-level Word file detection, version detection, initialization dispatch, and cleanup.

Key responsibilities:
- Checks file signatures for Word for DOS, OLE Word, RTF, WordPerfect, WinWord 1/2, and MacWord 4/5.
- Guesses a broad document family from magic bytes.
- Reads FIB version numbers to classify Word versions 0, 1, 2, 4, 5, 6, 7, or 8.
- Tracks whether the current document is an old Macintosh Word file.
- Dispatches initialization to DOS, Win, Mac, or OLE handlers.
- Frees all document-level lists and metadata with `vFreeDocument()`.

Important behavior:
- OLE detection tolerates one or two trailing bytes from buggy email/base64 handling in limited cases.
- Word 6 Macintosh detection uses `chse` and sets the old-Mac flag.
- Unknown FIB values below 192 are rejected; 192 and above are treated as Word 8-era.

Dependencies:
- All document initializers and all list destructors.

Research relevance:
- The front door and teardown point for Antiword document processing.
