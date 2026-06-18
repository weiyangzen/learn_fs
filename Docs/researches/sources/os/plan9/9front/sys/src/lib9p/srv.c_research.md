# File Research: sources/os/plan9/9front/sys/src/lib9p/srv.c

## Read Status
Complete: 948 lines read.

## Purpose
Core lib9p 9P server engine. It reads 9P messages, manages request/fid lifetimes, dispatches protocol operations to server callbacks or default tree-backed handlers, writes responses, handles flushes, negotiates msize, and closes server resources.

## Main Responsibilities
- Read and decode 9P messages from `Srv.infd`.
- Allocate active `Req` objects keyed by tag.
- Dispatch all major 9P2000 messages: version, auth, attach, flush, walk, open, create, read, write, clunk, remove, stat, and wstat.
- Provide default behavior for tree-backed servers.
- Enforce fid state, open modes, directory rules, offset/count bounds, and permissions.
- Call server callback hooks where supplied.
- Perform response post-processing per message type.
- Serialize responses and write them to `Srv.outfd`.
- Handle delayed `Tflush` responses.
- Manage server worker references and cleanup.

## Important Functions
- `srv`: initializes formatters, pools, msize buffers, callbacks, forker, refs, and enters `srvwork`.
- `srvwork`: main read/dispatch loop.
- `getreq`: reads one 9P message, decodes it, allocates a request, and handles duplicate tags.
- `respond`: central response finalizer and writer; performs message-specific completion hooks.
- `responderror`: responds with current system error string.
- `walkandclone`: helper for callback-based walk/clone servers.
- `srvacquire`, `srvrelease`: external locking/reference helpers.
- `srvclose`: frees server buffers and pools after refs drain.

## Protocol Dispatch Helpers
- `sversion`/`rversion`: version negotiation and msize update.
- `sauth`/`rauth`: auth fid allocation and cleanup.
- `sattach`/`rattach`: attach fid allocation and tree root setup.
- `sflush`/`rflush`: flush lookup and delayed response handling.
- `swalk`/`rwalk`: fid walking, cloning, partial walk behavior, and default tree walks.
- `sopen`/`ropen`: permission checking, directory constraints, iounit calculation, and open state.
- `screate`: create prechecks and callback dispatch.
- `sread`/`rread`: read checks, iounit clamping, directory read support, diroffset update.
- `swrite`/`rwrite`: write checks and qid version bump.
- `sclunk`/`rclunk`: fid removal.
- `sremove`/`rremove`: remove permission and tree removal.
- `sstat`/`rstat`: stat preparation and serialized stat output.
- `swstat`/`rwstat`: wstat validation and callback dispatch.

## Dependencies and Interactions
- Uses `fid.c`, `req.c`, `file.c`, `uid.c`, and `mem.c`.
- Uses 9P serialization APIs: `read9pmsg`, `convM2S`, `convS2M`, `convD2M`, `convM2D`, `sizeD2M`.
- Uses Plan 9 locks, refs, setjmp/longjmp, and fcall/dir formatters.
- Tree-backed default behavior is activated when `srv->tree` is set.
- Callback-based behavior is activated through fields such as `auth`, `attach`, `walk`, `walk1`, `clone`, `open`, `create`, `read`, `write`, `remove`, `stat`, `wstat`, `flush`, `start`, `end`, `free`.

## Notes
- `Tversion` is only accepted while the request ref count indicates the first request.
- Response generation converts successful replies to request type + 1; errors become `Rerror`.
- `respond` closes/removes requests before writing responses for pooled requests, then releases flush waiters and request/server refs.
- Service concurrency is bounded with `sref`; workers can stop when the server has many refs and they are not the original process.
