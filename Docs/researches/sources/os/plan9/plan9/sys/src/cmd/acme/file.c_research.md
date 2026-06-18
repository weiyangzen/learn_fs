# File Research: sources/os/plan9/plan9/sys/src/cmd/acme/file.c

This file wraps `Buffer` with file identity, shared text views, modification state, and undo/redo logs.

Key behavior:
- `fileaddtext()` and `filedeltext()` manage the list of `Text` views sharing a file.
- `fileinsert()` and `filedelete()` modify the buffer and emit inverse records when undo is active.
- `fileundelete()`, `fileuninsert()`, and `fileunsetname()` write undo records to delta/epsilon buffers.
- `fileundo()` replays undo or redo records backward, updating all associated text views.
- `filesetname()`, `fileload()`, `filereset()`, `fileclose()`, and `filemark()` manage lifecycle and sequence state.

Important details:
- Undo records are stored after associated data so the log can be read backward.
- `delta` is undo history; `epsilon` is redo history.
- Sequence numbers group simultaneous changes across files/windows.
- A `File` acts like a plain `Buffer` while `seq == 0`.

Filesystem relevance:
- Represents file-backed editor buffers and tracks state needed for safe writes/reloads.
