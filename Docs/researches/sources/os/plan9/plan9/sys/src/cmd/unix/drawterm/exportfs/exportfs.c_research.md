# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/exportfs/exportfs.c

Read fully: 511 lines, 8414 bytes. SHA-256 prefix: `32a938bacbd12b80`.

This file is the front end and state manager for drawterm’s 9P export service. It reads 9P messages from the CPU connection, dispatches them, tracks fids/files/qids, and sends replies.

Important routines:
- `exportfs()` installs the 9P handler table, initializes work buffers, fid hash, formatting, root file state, then loops on `read9pmsg()` and `convM2S()`.
- `reply()` builds `R*` or `Rerror` messages and writes them to the network.
- `newfid()`, `getfid()`, and `freefid()` manage fid hash entries and file references.
- `getsbuf()` allocates/reuses `Fsrpc` work buffers lazily.
- `file()`, `freefile()`, `initroot()`, and `makepath()` maintain a cached file tree rooted at `.`.
- `uniqueqid()`, `qidlookup()`, `qidexists()`, and `freeqid()` create stable unique exported qids when local dev/type/path combinations collide.
- `fatal()` reports and exits.

Risk notes: several locking and child-process note paths are commented out; this version relies on drawterm’s local runtime assumptions.
