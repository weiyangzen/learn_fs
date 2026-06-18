# File Research: sources/os/plan9/9front/sys/src/cmd/acme/dat.h

This is Acme's central data-definition header.

Key contents:
- Qid/file enum for the Acme 9P namespace: global files (`cons`, `index`, `log`, `new`, etc.) and per-window files (`addr`, `body`, `ctl`, `data`, `event`, `tag`, `xdata`, etc.).
- Constants for buffer block sizing, regex range count, UI dimensions, event size, and booleans.
- Core structs:
  - `Block`, `Disk`, `Buffer` for temp-file-backed text storage.
  - `Elog` for pending edit-command changes.
  - `File` for text contents, undo/redo buffers, names, stat metadata, text views, and modification state.
  - `Text` for visible frame state, selection, cache, scroll rectangle, and owning window/row/column.
  - `Window`, `Column`, `Row` for Acme's UI hierarchy.
  - `Command` for external child processes.
  - `Dirtab`, `Mntdir`, `Fid`, `Xfid` for the synthetic 9P server.
  - `Reffont`, `Rangeset`, `Dirlist`, `Expand`, `Timer`.
- Function prototypes for buffer, disk, file, text, window, column, row, 9P, font, and regex operations.
- Global variables for UI state, channels, filesystem state, font names, snarf, disk, active selections, and process-control channels.

Filesystem/storage relevance:
- Defines the synthetic filesystem contract and the storage model used by Acme.
- `File` records `qidpath`, `mtime`, and `dev` to detect on-disk modifications before writing.
- `Mntdir` captures per-command mount context and include paths.

Notes:
- `QID(w,q)`, `WIN(q)`, and `FILE(q)` encode/decode window id and file id in Qid paths.
- `File` embeds `Buffer`, making text content and buffer operations share layout directly.
