# File Research: sources/os/plan9/plan9/sys/src/cmd/ed.c

Plan 9 line editor implementation.

Key behavior:
- Maintains the edited buffer as line addresses pointing into a temporary file under `/tmp/eXXXXX`.
- Stores runes in 4096-byte blocks with separate input/output block caches.
- Implements classic `ed` commands: append, change, delete, edit/read/write, filename, global/inverse global, insert, join, mark, move/copy, print/list/number, quit, shell escape, substitute, undo-last-substitution, and line addressing.
- Uses Plan 9 `Biobuf` and rune-aware I/O for files and terminal input.
- Handles regular expressions via `regexp.h`, including substitutions with `&` and numbered submatches.
- On hangup, writes current buffer to `ed.hup` if possible.
- Warns on append-only input files and supports append writes via `W`.

Filesystem relevance:
- File editor with explicit temp-file storage, read/write/create/append behavior, and crash/hangup rescue path.
