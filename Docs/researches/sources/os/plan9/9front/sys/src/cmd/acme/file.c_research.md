# File Research: sources/os/plan9/9front/sys/src/cmd/acme/file.c

This file implements `File` lifecycle, text-view association, undo/redo logs, name changes, and low-level buffer mutation.

Key responsibilities:
- `fileaddtext()` creates a `File` if needed and associates a `Text` view.
- `filedeltext()` removes a `Text`; closes the file when the last view is gone.
- `fileinsert()`/`filedelete()` mutate file content and record inverse operations in `delta` when undo is active.
- `fileuninsert()` and `fileundelete()` serialize undo records and deleted text.
- `filesetname()` and `fileunsetname()` change names and record undo information.
- `fileload()` loads from fd into the file buffer when undo is inactive.
- `fileredoseq()` reports the sequence number pending in redo state.
- `fileundo()` replays `delta` or `epsilon` records, updating all associated text views.
- `filereset()`, `fileclose()`, and `filemark()` reset/close/mark undo state.

Important dependencies:
- Uses `Buffer` for content and undo logs.
- Uses `textinsert()`/`textdelete()` to keep all views synchronized during undo/redo.
- Uses global `seq` for grouping simultaneous changes.

Filesystem/storage relevance:
- `File` tracks on-disk identity metadata but this file mainly handles in-memory/buffer state and undo.
- Provides the mutation layer used by text editing and disk I/O callers.

Notes:
- Undo records are stored after their associated data so the log can be read backward.
- Multiple `Text` views over the same `File` are first-class and updated together.
