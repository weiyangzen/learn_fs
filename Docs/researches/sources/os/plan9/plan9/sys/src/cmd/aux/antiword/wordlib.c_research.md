# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/antiword/wordlib.c

This file provides common Word file identification, version detection, document initialization dispatch, and cleanup.

Key behavior:
- Checks file signatures for Word for DOS, WinWord 1/2, Mac Word 4/5, OLE Word files, RTF, and WordPerfect.
- Maps FIB/version header values to Antiword version numbers.
- Tracks old Macintosh Word files for character translation behavior.
- Dispatches initialization to DOS, Windows, Mac, or OLE handlers.
- `vFreeDocument()` destroys every global parsing/rendering list.

Important details:
- OLE file detection tolerates certain extra trailing bytes caused by buggy email/base64 handling.
- Unknown FIB values below Word 97 are rejected; newer values are treated as Word 8 format.

Filesystem relevance:
- Direct file signature inspection and top-level file-format dispatch.
