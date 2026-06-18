# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/drawterm/kern/exportfs.c

Implements a local exportfs server: it serves the current namespace over a 9P-like stream.

Key behavior:
- `sysexport(fd)` wraps an open fd as the transport, captures the current process group and root, and enters `exportproc`.
- Reads incoming messages, handles partial message carryover, decodes `Fcall`s, and dispatches them to worker threads.
- Maintains `Export` state with root channel, io channel, process group, active fid hash, and work queue.
- Handles `Tflush` by removing queued work or interrupting in-progress work and sending `Rflush`.
- Worker threads run requests in the exported process group, dispatch through the `fcalls` table, and serialize replies.
- Tracks `Fid` objects with reference counts, attached state, and underlying `Chan`.

Implemented operations:
- `Tversion`, `Tauth`, `Tattach`, `Twalk`, `Topen`, `Tcreate`, `Tread`, `Twrite`, `Tclunk`, `Tremove`, `Tstat`, and `Twstat`.
- Authentication is not required.
- Reads and writes dispatch to the underlying device operations on the local channel.

Notable risks:
- `Nfidhash` is 1, so all fids share one hash bucket.
- The file contains older protocol assumptions such as `DIRLEN` alignment for directory reads.
- Some shutdown interruption logic is commented or diagnostic-only.
