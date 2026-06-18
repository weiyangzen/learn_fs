# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/exportfs/exportsrv.c

Read fully: 676 lines, 11048 bytes. SHA-256 prefix: `f6be7b01ce2762f0`.

This file implements drawterm exportfs’s 9P request handlers and blocking I/O worker path.

Handlers:
- `Xversion()` negotiates `9P2000` and message size.
- `Xauth()` rejects auth because authentication is handled before exportfs.
- `Xflush()` marks or replies to flush requests.
- `Xattach()` attaches fids to the exported root.
- `Xwalk()` walks path elements, cloning fids when requested.
- `Xclunk()`, `Xstat()`, `Xcreate()`, `Xremove()`, and `Xwstat()` map 9P operations to local Plan 9 file operations.
- `slave()` starts/reuses worker processes for potentially blocking `Topen`, `Tread`, and `Twrite`.
- `blockingslave()` dispatches to `slaveopen()`, `slaveread()`, and `slavewrite()`.
- `flushaction()` handles notes in the worker context.

Risk notes: comments acknowledge races and unimplemented mount traversal (`openmount()` returns an error). This is sufficient for drawterm’s exported namespace use case, not a general hardened 9P server.
