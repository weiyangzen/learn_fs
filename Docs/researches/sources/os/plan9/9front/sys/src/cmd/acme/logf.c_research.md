# File Research: sources/os/plan9/9front/sys/src/cmd/acme/logf.c

This file implements Acme's global event log file, exposed through the synthetic namespace.

Key responsibilities:
- Defines `Log`, containing a queued event list, reader fids, blocked read xfids, sequence offset, and synchronization state.
- `xfidlogopen()` registers a fid and positions it at the current log end.
- `xfidlogclose()` unregisters a fid.
- `xfidlogread()` blocks until a new event is available or the read is flushed, then responds with one event line.
- `xfidlogflush()` marks matching blocked reads as flushed and wakes readers.
- `xfidlog(w, op)` appends an event line of the form `<winid> <op> <name>\n`, compacts events all readers have consumed, grows storage as needed, and wakes readers.

Important dependencies:
- Uses `Window`, `File`, `Fid`, `Xfid`, `respond()`, `runetobyte()`, and locking/rendezvous primitives.
- Called by window lifecycle, Get/Put, focus, and Zerox paths.

Filesystem/storage relevance:
- Provides `/mnt/acme/log` style event streaming for external programs.
- Tracks file/window operations without reading individual per-window event files.

Notes:
- Expected operations include `new`, `zerox`, `get`, `put`, `del`, and `focus`.
- Log retention is bounded by slowest active reader; when all readers advance, consumed entries are freed.
