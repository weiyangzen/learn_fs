# File Research: sources/os/plan9/plan9/sys/src/cmd/acme/dat.h

This is Acme’s central data definition header.

Key contents:
- Qid constants for global and per-window 9P files: `cons`, `index`, `new`, `addr`, `body`, `ctl`, `data`, `event`, `rdsel`, `wrsel`, `tag`, `xdata`, etc.
- Storage constants: `Blockincr`, `Maxblock`, `NRange`, `Infinity`.
- Core structs: `Block`, `Disk`, `Buffer`, `Elog`, `File`, `Text`, `Window`, `Column`, `Row`, `Timer`, `Command`, `Dirtab`, `Mntdir`, `Fid`, `Xfid`, `Reffont`, `Rangeset`, `Dirlist`, `Expand`.
- Function prototypes for disk, buffer, edit log, file, text, window, row, column, xfid, and font APIs.
- Global variables for display state, row/window focus, disk, snarf buffer, fonts, plumber fds, channels, and editing flags.

Important details:
- `File` embeds `Buffer` and adds undo/redo logs plus shared text views.
- `Text` embeds `Frame`, linking storage to screen representation.
- `Window` holds per-9P-open counts, event buffers, address state, include directories, dump metadata, and lock/ref state.
- `Mntdir`, `Fid`, and `Xfid` define Acme’s in-process 9P server state.

Filesystem relevance:
- Foundational: defines the Acme pseudo-filesystem namespace and backing data model.
