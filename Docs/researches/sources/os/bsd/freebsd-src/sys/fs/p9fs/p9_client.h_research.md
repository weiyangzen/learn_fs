# File Research: sources/os/bsd/freebsd-src/sys/fs/p9fs/p9_client.h

This header defines the public 9P client structures and APIs used by p9fs.

Key types:
- `enum p9_proto_versions`: legacy `9P2000`, Unix `9P2000.u`, and Linux `9P2000.L`.
- `struct p9_req_t`: transmit and receive buffers for one 9P request.
- `enum transport_status`: connected, begin-disconnect, disconnected.
- `struct p9_client`: transport ops/handle, mutexes, request CV, msize, protocol version, fid/tag pools, and transport state.
- `struct p9_fid`: local fid object with numeric fid, mode, qid, MTU, uid, open count, and list linkage.
- `struct p9_dirent`: parsed 9P directory entry.

Constants:
- `P9FS_MTU` is 131072.
- `P9FS_IOUNIT` is `P9FS_MTU - 24`.
- `P9FS_DIRENT_LEN` is 256.
- `P9_NOTAG` is 0.

Exported APIs:
- Zone lifecycle: `p9_init_zones()`, `p9_destroy_zones()`.
- Client/session lifecycle: `p9_client_create()`, `p9_client_destroy()`, `p9_client_attach()`.
- Fid/tag helpers: `p9_fid_create()`, `p9_fid_destroy()`, `p9_tag_create()`, `p9_tag_destroy()`.
- Protocol requests for open, close/clunk, walk, readdir, read/write, create, remove, unlink, statfs, symlink, hardlink, readlink, renameat, getattr, setattr.
- Buffer helpers: `p9_buf_vwritef()`, `p9_buf_readf()`, `p9_buf_prepare()`, `p9_buf_finalize()`, `p9_buf_reset()`.

Research-relevant notes:
- This header is the contract between p9fs vnode/mount code and the transport/protocol implementation.
- It exposes negative-error/positive-byte-count conventions for read/write through return types rather than separate output parameters.
