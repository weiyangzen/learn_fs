# File Research: sources/os/plan9/plan9/sys/src/cmd/acme/xfid.c

Implements Acme filesystem fid operations for window pseudo-files: open, close, read, write, flush, event I/O, address I/O, and index reads.

Key functions:
- `xfidctl` is the worker loop receiving operation functions on an `Xfid` channel.
- `xfidopen` initializes per-qid state for `addr`, `data`, `xdata`, `event`, `rdsel`, `wrsel`, and `editout`.
- `xfidclose` reverses open state, releases exclusive ctl locks, restores menus, closes temp selection fds, and decrefs windows.
- `xfidread` dispatches reads for window body/tag text, control metadata, addr, data, selected text, event stream, and global index.
- `xfidwrite` dispatches writes to console, label, addr, editout, errors, body, selected text, ctl, data, events, and tag.
- `xfidctlwrite` parses textual control commands such as `lock`, `unlock`, `clean`, `dirty`, `show`, `name`, `dump`, `dumpdir`, `delete`, `del`, `get`, `put`, `dot=addr`, `addr=dot`, `limit=addr`, `nomark`, `mark`, `nomenu`, `menu`, `noscroll`, `cleartag`, and `scroll`.
- `xfideventread` blocks on window event availability and handles flush/shutdown wakeups.
- `xfidutfread`, `xfidruneread`, and `fullrunewrite` preserve UTF-8/rune boundaries.

Interactions:
- Uses `Window` state from `wind.c`, including `addr`, `limit`, `events`, `eventx`, `nopen`, `wrselrange`, `filemenu`, and dirty flags.
- Calls Acme editing/search helpers such as `address`, `execute`, `look3`, `edittext`, `cut`, `get`, and `put`.

Notable details:
- Read selection uses a temp file rather than a pipe to avoid broken-pipe behavior and mutation races.
- UTF reads cache the last byte/rune offset per qid to avoid always rescanning from the beginning.
- Event writes encode actions through Acme’s external event protocol and execute/look selected tag/body regions.
