# File Research: sources/os/bsd/dragonflybsd/sys/vfs/nfs/nfs_serv.c

This is the main NFSv2/NFSv3 server operation implementation. Each RPC handler follows the same broad pattern: decode request fields from mbufs, translate file handles or names to vnodes, execute VFS/VOP operations, and build XDR replies with NFSv2/NFSv3-specific status and attribute payloads.

Major server handlers:
- Metadata and access: `nfsrv3_access()`, `nfsrv_getattr()`, `nfsrv_setattr()`.
- Name/file operations: `nfsrv_lookup()`, `nfsrv_create()`, `nfsrv_mknod()`, `nfsrv_remove()`, `nfsrv_rename()`, `nfsrv_link()`, `nfsrv_symlink()`, `nfsrv_mkdir()`, `nfsrv_rmdir()`.
- Data operations: `nfsrv_readlink()`, `nfsrv_read()`, `nfsrv_write()`, `nfsrv_writegather()`.
- Directory operations: `nfsrv_readdir()`, `nfsrv_readdirplus()`.
- Filesystem queries: `nfsrv_commit()`, `nfsrv_statfs()`, `nfsrv_fsinfo()`, `nfsrv_pathconf()`.
- Generic procedures: `nfsrv_null()`, `nfsrv_noop()`.

Key support logic:
- `nfsrv_sequential_heuristic()` tracks per-vnode sequential read/write behavior and feeds sequence hints into I/O flags.
- `nfsrv_writegather()` delays and coalesces adjacent writes for throughput, using per-service-socket delay queues.
- `nfsrvw_coalesce()` merges overlapping/contiguous write mbuf chains and links coalesced descriptors for later replies.
- `nfsrv_access()` implements server-side permission checks, including export read-only state and limited owner override semantics.

Important behavior:
- NFSv3 weak cache consistency data is collected around mutating operations through pre/post attributes.
- Public file handle/WebNFS lookup is supported in `nfsrv_lookup()`, including index-file redirection and mount-boundary checks.
- Directory reads filter zero inode and whiteout entries, manage cookies, and pack replies tightly with `nfsm_clget()`.
- `nfsrv_readdirplus()` additionally resolves each directory entry to attributes and file handles through `VFS_VGET()` and `VFS_VPTOFH()`.
- `nfsrv_commit()` flushes dirty VM pages and buffers, either whole-file or aligned range, and returns the write verifier.

Important interactions:
- Relies heavily on macros and helpers from `nfsm_subs.h` and `nfs_subs.c`.
- File-handle translation and export enforcement are delegated to `nfsrv_fhtovp()`.
- Name operations are delegated to `nfs_namei()`, then DragonFly namecache/VOP calls such as `VOP_NCREATE`, `VOP_NREMOVE`, `VOP_NRENAME`, `VOP_NLINK`, `VOP_NSYMLINK`, `VOP_NMKDIR`, and `VOP_NRMDIR`.
- RPC procedure dispatch is registered from `nfs_socket.c` through `nfsrv3_procs`.

Caveats:
- Cleanup is subtle because many `nfsm_*` macros jump to `nfsmout`; each handler carefully tracks vnode, mount, mbuf, namecache, and allocation ownership.
- NFSv2 and NFSv3 behavior is interleaved, so reply size and error paths must preserve protocol-specific semantics.
- Some comments document legacy or incomplete behavior, such as metadata sync semantics, cookie verifier strictness, and VOP offset limits for commit.
