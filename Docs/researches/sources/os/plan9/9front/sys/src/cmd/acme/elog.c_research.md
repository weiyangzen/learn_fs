# File Research: sources/os/plan9/9front/sys/src/cmd/acme/elog.c

This file implements deferred edit logs for Acme edit commands.

Key responsibilities:
- `eloginit()` initializes a file's edit log buffer and scratch rune buffer.
- `elogclose()` releases the edit log buffer.
- `elogreset()`/`elogterm()` reset or fully tear down pending log state.
- `elogflush()` serializes the pending in-memory `Elog` entry into the log buffer.
- `elogreplace()`, `eloginsert()`, and `elogdelete()` record deferred modifications and merge nearby compatible changes when possible.
- `elogapply()` replays the log into the file's current text, marking undo state once, applying text insert/delete operations, adjusting selections, and restoring window ownership.

Important dependencies:
- Uses `Buffer` to store serialized `Buflog` entries and replacement/insert strings.
- Uses `textinsert()`, `textdelete()`, `textconstrain()`, `filemark()`, and `winsettag()` via update paths.
- Called by `edit.c` and `ecmd.c`.

Filesystem/storage relevance:
- This is Acme's transaction layer for editing file buffers. It avoids applying edits while addresses are still being interpreted against the old file state.

Notes:
- Warns once for out-of-sequence changes but attempts to continue.
- Merges replacements when gaps are small and total merged text fits in `RBUFSIZE`.
