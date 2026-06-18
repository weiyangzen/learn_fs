# File Research: sources/os/bsd/freebsd-src/sys/fs/p9fs/p9fs_subr.c

This file implements p9fs non-VFS helper routines for session lifecycle and fid management.

Key functions:
- `p9fs_proto_dotl()` checks whether a session negotiated `9P2000.L`.
- `p9fs_init_session()` creates the 9P client, records negotiated protocol flags, parses `access=`, attaches to the server, initializes the session node list and lock, and returns the mount fid.
- `p9fs_prepare_to_close()` breaks node parent references and begins client disconnect, allowing only cleanup clunks afterward.
- `p9fs_complete_close()` marks the client disconnected.
- `p9fs_close_session()` completes disconnect, destroys the client, destroys the session lock.
- `p9fs_fid_add()`, `p9fs_fid_remove()`, and `p9fs_fid_remove_all()` manage per-node fid lists and clunk removed fids.
- `p9fs_get_fid()` finds or creates a fid for a node/user/type/mode by attaching as needed and walking from root to the node.
- Internal helpers build full root-to-node path arrays and test whether an existing open fid is compatible with a requested mode.

Access modes:
- `access=any`: reuse the session uid.
- `access=single`: session flag is set but uid selection still falls through to credential uid unless handled elsewhere.
- `access=user`: attach per user; this is the default.

Research-relevant risks:
- `p9fs_get_fid()` walks path chunks of at most `P9_MAXWELEM`, but passes the same `wnames` base pointer each time rather than offsetting by `i`; that is notable for path lengths over one chunk.
- `p9fs_fid_remove_all()` walks/removes lists without taking the per-list locks used by add/remove helpers.
- Parent references are broken during close to avoid vnode reference cycles before flush.
