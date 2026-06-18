# File Research: sources/os/bsd/freebsd-src/sys/fs/nfsclient/nfs.h

`nfsclient/nfs.h` is the public-ish kernel client header for FreeBSD's NFS client support functions, debug hooks, and async I/O daemon state.

Key contents:
- Defines terminal print delay defaults `NFS_TPRINTF_INITIAL_DELAY` and `NFS_TPRINTF_DELAY`.
- Defines vnode mount version predicates `NFS_ISV3`, `NFS_ISV4`, and `NFS_ISV34`.
- Under `NFS_DEBUG`, defines debug categories and `NFS_DPF`; otherwise it compiles to no-op.
- Defines `enum nfsiod_state` with states for unavailable, available, and newly created-for-async-I/O nfsiod threads.
- Declares client BIO/page/cache functions: `ncl_meta_setsize`, `ncl_bioread`, `ncl_biowrite`, `ncl_vinvalbuf`, `ncl_asyncio`, `ncl_doio`.
- Declares node lifecycle/cache functions: `ncl_nhinit`, `ncl_nhuninit`, `ncl_nodelock`, `ncl_nodeunlock`, `ncl_getattrcache`.
- Declares RPC operations for read, write, readlink, readdir, readdirplus, commit, clearcommit, fsinfo.
- Declares module init/uninit and nfsiod creation functions.

Important integration points:
- This header connects vnode operations to the client-side RPC implementation and async I/O subsystem.
- The function list spans files in this group (`nfs_clbio.c`, `nfs_clnode.c`, `nfs_clnfsiod.c`) and other client RPC files outside this group.

Research notes:
- The header is declaration-focused; behavior lives in the client `.c` files.
