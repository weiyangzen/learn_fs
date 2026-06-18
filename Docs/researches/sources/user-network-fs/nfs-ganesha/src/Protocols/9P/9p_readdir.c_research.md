## sources/user-network-fs/nfs-ganesha/src/Protocols/9P/9p_readdir.c

Purpose: implements directory enumeration for 9P.

APIs and flow: `_9p_readdir` validates fid/msize/count, initializes op context, emits synthetic `.` and `..` entries for offsets 0/1, converts cookies, then calls `fsal_readdir` with `_9p_readdir_callback`. The callback maps FSAL object types to 9P qid type and VFS `d_type`, stops before the reply buffer limit, and encodes directory entries.

State/dependencies: read-only over directory object state, but uses FSAL lookup-parent refs and readdir cookies. Reply size accounting is local to `_9p_cb_data`.

Risks/tests: test small count handling, dot/dotdot offsets, cookie continuation, buffer-full truncation, unknown object types, parent lookup failure, and consistency of returned dcount.
