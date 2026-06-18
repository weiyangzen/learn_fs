# File Research: sources/os/bsd/freebsd-src/sys/fs/p9fs/p9fs.h

This header defines the p9fs filesystem’s in-memory mount, session, node, and inode structures.

Key structures:
- `struct p9fs_qid`: p9fs-local qid mirror.
- `struct p9fs_inode`: cached remote inode metadata, including mode, type, size, timestamps, ownership strings/numeric IDs, qid path, link count, block info, generation, and data version.
- `struct p9fs_node`: per-vnode p9fs node containing VFID and VOFID lists, locks, parent pointer, qid, vnode pointer, inode cache, session pointer, session list linkage, and flags.
- `struct p9fs_session`: per-mount session state, including root node, mount pointer, access identity, 9P client, session lock, node list, mount fid, and name length cache.
- `struct p9fs_mount`: mount wrapper containing the session and mount tag.

FID model:
- `VFID` identifies general vnode fids.
- `VOFID` identifies open fids.
- Separate mutex-protected STAILQ lists track fids by node and uid/mode.

Flags:
- Node flags include modified, root, deleted, and in-session.
- Session flags include protocol version and access mode (`any`, `single`, `user`).

Exported filesystem helpers:
- Session lifecycle: `p9fs_init_session()`, `p9fs_prepare_to_close()`, `p9fs_complete_close()`, `p9fs_close_session()`.
- Node/vnode lookup and lifecycle: `p9fs_vget()`, `p9fs_vget_common()`, `p9fs_node_cmp()`, `p9fs_destroy_node()`, `p9fs_dispose_node()`, `p9fs_cleanup()`.
- Fid management: `p9fs_fid_add()`, `p9fs_fid_remove()`, `p9fs_fid_remove_all()`, `p9fs_get_fid()`.
- Attribute helpers: `p9fs_stat_vnode_dotl()`, `p9fs_reload_stats_dotl()`, `p9fs_proto_dotl()`.

Research-relevant notes:
- Parent pointers are reference-counted through vnode refs and explicitly broken during unmount preparation.
- The filesystem uses qid path/version/type for vnode identity.
- Root node is embedded in the session; non-root nodes are UMA allocated.
