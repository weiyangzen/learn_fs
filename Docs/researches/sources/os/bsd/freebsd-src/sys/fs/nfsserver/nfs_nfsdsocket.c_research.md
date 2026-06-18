# File Research: sources/os/bsd/freebsd-src/sys/fs/nfsserver/nfs_nfsdsocket.c

## Role

`nfs_nfsdsocket.c` is the NFS server RPC dispatch and NFSv4 COMPOUND execution layer. It maps NFS procedure/op numbers to the service handlers in `nfs_nfsdserv.c`, performs file-handle-to-vnode setup for NFSv2/v3, manages NFSv4 current and saved file handles, tracks server RPC statistics, and handles several global NFSv4 state-maintenance tasks before and during COMPOUND processing.

Despite the filename, the file is less about raw sockets and more about request dispatch after transport-level receive has produced an `nfsrv_descript`.

## Dispatch Tables

The file defines the server operation tables consumed by the dispatcher:

- `nfsrv3_procs0`: NFSv3 operations using one current file handle, such as getattr, setattr, access, readlink, read, write, create, remove/rmdir, readdir, statfs, fsinfo, pathconf, and commit.
- `nfsrv3_procs1`: NFSv3 operations that return a new file handle, such as lookup, mkdir, symlink, and mknod.
- `nfsrv3_procs2`: NFSv3 operations using two file handles, primarily rename and link.
- `nfsrv4_ops0`: NFSv4 operations using no returned file handle or only the current file handle, including access, close, commit, delegation operations, getattr, lock operations, read/write, state/session operations, layouts, NFSv4.2 allocation/deallocation/seek/xattrs, and unsupported stubs.
- `nfsrv4_ops1`: NFSv4 operations that can return a new current file handle, including create, lookup, open, and openattr.
- `nfsrv4_ops2`: NFSv4 operations needing current and saved file handles, including link, rename, copy, and clone.

The file also defines `nfsrv_nonidempotent[]`, `nfsrv_writerpc[]`, `nfs_retfh[]`, and `nfsv3to4op[]` to drive reply caching, write-start behavior, handler signatures, and statistics mapping.

## Statistics

`nfsrvd_statstart()` and `nfsrvd_statend()` maintain per-VNET NFS server counters:

- RPC start/done counts.
- Per-operation request counts.
- Per-operation completed operation counts.
- Byte counts.
- Cumulative operation duration.
- Busy-time accounting.

The functions serialize updates with `nfsrvd_statmtx` and validate operation indexes against the NFSv4.2 op range plus fake stat slots.

## NFSv2/v3 Dispatch

`nfsrvd_dorpc()` is the top-level dispatcher for non-COMPOUND requests and the entry point that delegates NFSv4 to `nfsrvd_compound()`.

For NFSv2/v3 it:

- Saves request mbuf position so an `ERELOOKUP` retry can rewind and redo the operation.
- Decodes the file handle with `nfsrv_mtofh()`.
- Chooses shared locks for read-like operations and exclusive locks for mutating or ambiguous operations.
- Calls `nfsd_fhtovp()` with public-filehandle handling if `ND_PUBLOOKUP` is set.
- Marks non-idempotent operations for reply caching.
- Builds the reply head.
- Selects the correct handler table using `nfs_retfh[]`.
- Performs retry on `ERELOOKUP` by freeing the partial reply and replaying from the saved request position.
- Maps `nd_repstat` through `nfsd_errmap()`.
- Suppresses reply-cache saving for transient or non-cacheable status values.

## NFSv4 COMPOUND Execution

`nfsrvd_compound()` parses and executes NFSv4 COMPOUND calls. It manages:

- Tag echoing and operation count parsing.
- Minor-version validation against `vfs.nfsd.server_min_minorversion4` and `server_max_minorversion4`.
- Root/state lock/reference coordination for NFSv4 global state.
- Stable storage updates after grace period completion.
- Expired-client cleanup and delegation cleanup.
- Open-owner cleanup and pNFS layout recall when layout count exceeds the high-water mark.
- Current file handle (`vp`) and saved file handle (`savevp`) lifetimes.
- Export data for current/saved file handles.
- Current and saved current-stateid handling for `SAVEFH` and `RESTOREFH`.

The operation loop enforces NFSv4.1 sequencing rules: `SEQUENCE` must be first except for a small set of session-establishment/destruction operations; operations after a non-`SEQUENCE` first op are rejected where required.

## File Handle Handling

The COMPOUND dispatcher implements operation-local behavior for:

- `PUTFH`: parses a file handle, looks up a vnode, and sets current FH.
- `PUTPUBFH`: uses the global public file handle if configured.
- `PUTROOTFH`: uses the VNET root file handle if configured.
- `SAVEFH`: references the current vnode and export data as saved FH.
- `RESTOREFH`: restores the saved vnode/export state and saved current-stateid if present.

It also pre-parses following op numbers around `PUTFH`, `PUTPUBFH`, `PUTROOTFH`, and `RESTOREFH` to handle `SAVEFH` chains and to decide when `NFSERR_WRONGSEC` checks are allowed.

## Security and Resource Controls

The dispatcher checks several cross-cutting conditions before invoking handlers:

- Operation legality by NFS minor version.
- Referral handling, returning `NFSERR_MOVED` for allowed operations on referral file handles.
- NFSv4.1 session operation ordering.
- Memory/reply-cache flood conditions using `nfsrv_mallocmget_limit()` and `nfsrc_tcpsavedreplies`.
- `SP4_MACH_CRED` behavior: when `ND_MACHCRED` is set and the op is in the allowed set, credentials are temporarily replaced with root credentials from `nfsrv_createrootcred()`.

`nfsrv_createrootcred()` creates a root credential in the current prison, sets wheel group, holds the prison reference, and attaches MAC credentials when MAC support is compiled in.

## Retry and Reply Trimming

Like NFSv3 dispatch, the COMPOUND loop supports retry on `ERELOOKUP`. Before invoking a normal operation it saves request and reply mbuf positions. On `ERELOOKUP`, it restores request position, trims the partial reply with `nfsm_trimtrailing()`, sets `ND_ERELOOKUP`, clears the status, and retries the operation.

This is important because several vnode/namecache operations can require relookup without causing a protocol-visible partial reply.

## Interaction With Service File

This file is the control plane for `nfs_nfsdserv.c`. It decides which `nfsrvd_*` handler to call, with what vnode arguments, what lock state, and whether the operation is allowed to mutate filesystems. The actual vnode work and protocol-specific reply payloads live in `nfs_nfsdserv.c`.

`nfsv4_opflag[]`, declared externally, is central to this relationship. It tells the dispatcher whether an op needs the current file handle, returns a file handle, modifies the filesystem, requires a specific lock type, or should be saved in the reply cache.

## Research Notes

The most important behavior in this file is not the procedure tables themselves but the sequencing and lifetime model around vnodes, saved file handles, root-state locking, reply caching, and retry. Any future modification to NFSv4 operation support must update the dispatch tables, `nfsv4_opflag[]` in its defining file, statistics mapping if relevant, and the service implementation together.
