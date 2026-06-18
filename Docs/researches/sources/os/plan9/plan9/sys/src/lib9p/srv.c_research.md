# File Research: sources/os/plan9/plan9/sys/src/lib9p/srv.c

This is the core lib9p 9P2000 server dispatcher. It reads incoming 9P messages, creates `Req` objects, dispatches by message type, applies generic fid/tree semantics, calls server callbacks, serializes responses, and cleans up pools.

Key behavior:
- Maintains global `_forker` used by listen/postmount helpers.
- `changemsize` resizes shared read/write buffers under locks.
- `getreq` reads a 9P message, decodes it into `Fcall`, allocates a tagged request, and creates a fake request for duplicate tags.
- `srv` initializes fmt handlers, fid/request pools, default msize, buffers, then loops over requests and dispatches `Tversion`, `Tauth`, `Tattach`, `Tflush`, `Twalk`, `Topen`, `Tcreate`, `Tread`, `Twrite`, `Tclunk`, `Tremove`, `Tstat`, and `Twstat`.
- Tree-backed operation support handles attach-to-root, file walking, permission checks, directory open/read, remove, stat copying, and qid/version updates.
- Callback-driven operation support allows servers to provide `auth`, `attach`, `flush`, `walk`, `walk1`, `clone`, `open`, `create`, `read`, `write`, `remove`, `stat`, and `wstat`.
- `respond` runs per-message postprocessing, converts errors to `Rerror`, serializes with `convS2M`, writes replies under `wlock`, removes requests from the pool, and releases delayed flush replies.
- `responderror` converts current `%r` state into a 9P error response.
- `postfd` posts a server fd under `/srv/<name>`.

Important dependencies:
- `fid.c`, `req.c`, `file.c`, `uid.c`, and `mem.c`.
- Plan 9 wire conversion: `read9pmsg`, `convM2S`, `convS2M`, `convD2M`, `convM2D`.
- Uses `fcallfmt` and `dirfmt` for debug output.

Notable details:
- Flush handling is special: a flush reply can be delayed until the old request responds.
- Partial walks are treated as successful with no error when at least one element was walked.
- Directory reads require offset zero or the current tracked directory offset.
- Wstat prevalidates immutable fields before calling the server’s `wstat`.
- The generic remove path removes the fid from the pool before invoking callbacks, matching 9P remove semantics.
