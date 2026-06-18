# File Research: sources/os/plan9/plan9/sys/src/cmd/vnc/exportfs.c

User-space 9P2000 export server for the synthetic VNC device roots.

Key responsibilities:
- Reads 9P messages, dispatches them to worker kprocs, and writes replies.
- Supports `Tversion`, `Tauth`, `Tattach`, `Twalk`, `Topen`, `Tcreate`, `Tread`, `Twrite`, `Tclunk`, `Tremove`, `Tstat`, `Twstat`, and `Tflush`.
- Maintains per-export fid hash tables with refcounts, attached state, channel pointers, and offsets.
- Queues work globally across exports and starts worker processes on demand.
- Handles flush by removing queued work or interrupting in-progress workers and suppressing their reply.
- Shuts down by draining queued work, interrupting sleepers, and freeing fids/channels.

Important behavior:
- `Tauth` always reports authentication not required.
- Attach spec selects one of the exported root channels numerically.
- Device operations are delegated through `devtab[c->type]`.
- Reads place response data directly in the 9P output buffer after `IOHDRSZ`.

Risks:
- Worker and flush synchronization is subtle: queued, active, responding, and no-response states are separate.
- Directory seek alignment checks are defined but not actually used in `Exread`.
