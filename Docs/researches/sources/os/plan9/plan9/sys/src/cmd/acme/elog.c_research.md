# File Research: sources/os/plan9/plan9/sys/src/cmd/acme/elog.c

This file implements Acme’s edit-command change log, separate from normal undo/redo.

Key behavior:
- `eloginit()`, `elogreset()`, `elogterm()`, and `elogclose()` manage per-file edit log state.
- `elogreplace()`, `eloginsert()`, and `elogdelete()` record pending changes against original buffer coordinates.
- `elogflush()` serializes current pending edit into `elogbuf`.
- `elogapply()` applies serialized changes to the current text/file, marking the file and updating display/selection.

Important details:
- The design explicitly preserves original-address semantics for edit commands and merges nearby changes to reduce I/O.
- Out-of-sequence changes warn once, flush the current change, and continue.
- Insert/replace text is chunked at `RBUFSIZE`.
- `elogapply()` constrains possibly stale/overlapping addresses before calling `textdelete()`/`textinsert()`.

Filesystem relevance:
- Important for safe scripted edits to file-backed buffers before writes happen.
