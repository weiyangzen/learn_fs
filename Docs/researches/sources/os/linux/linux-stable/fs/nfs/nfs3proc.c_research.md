# File Research: sources/os/linux/linux-stable/fs/nfs/nfs3proc.c

## Purpose
Implements client-side NFSv3 procedure stubs and exports the `nfs_v3_clientops` operation table used by the generic NFS client.

## RPC Wrapper and Retry
- `nfs3_rpc_wrapper()` wraps synchronous RPC calls to handle `-EJUKEBOX` by sleeping for `NFS_JUKEBOX_RETRY_TIME` unless interrupted or exiting.
- The file locally redefines `rpc_call_sync` to the wrapper.
- `nfs3_async_handle_jukebox()` restarts async tasks after delay and increments `NFSIOS_DELAY`.

## Core Metadata Procedures
- `nfs3_proc_get_root()` uses FSINFO and falls back to GETATTR if needed.
- `nfs3_proc_getattr()` optionally uses timeout behavior for soft revalidation.
- `nfs3_proc_setattr()` uses file credentials when available, updates inode state, and zaps ACL cache if ACL state was invalidated.
- Lookup:
  - `__nfs3_proc_lookup()` sends LOOKUP, refreshes parent directory attrs, and falls back to GETATTR if returned object attrs are absent.
  - `nfs3_proc_lookup()` adds soft-revalidation timeout behavior.
  - `nfs3_proc_lookupp()` looks up `".."`.

## Access and Readlink
- `nfs3_proc_access()` sends ACCESS, refreshes attrs, and maps returned access mask into `nfs_access_entry`.
- `nfs3_proc_readlink()` sends READLINK into a page buffer and refreshes symlink attrs.

## Create and Directory Mutations
- `struct nfs3_createdata` packages create-family args, result file handle, object attrs, and directory attrs.
- `nfs3_proc_create()`
  - Handles POSIX ACL creation.
  - Supports exclusive create with verifier, and falls back from exclusive to guarded to unchecked on `-ENOTSUPP`.
  - Performs post-create setattr after exclusive create.
  - Applies ACLs after creation.
- `nfs3_proc_remove()`, unlink setup/prepare/done, rename setup/prepare/done update post-op directory attrs.
- `nfs3_proc_link()` updates both file and target directory attrs.
- `nfs3_proc_symlink()`, `nfs3_proc_mkdir()`, `nfs3_proc_rmdir()`, and `nfs3_proc_mknod()` implement their VFS operations with appropriate create data and ACL handling.

## Readdir and Filesystem Info
- `nfs3_proc_readdir()` supports plain READDIR and READDIRPLUS, copies cookie verifier when cookie is nonzero, invalidates directory atime, and refreshes directory attrs.
- `nfs3_proc_statfs()`, `nfs3_proc_fsinfo()`, and `nfs3_proc_pathconf()` wrap FSSTAT, FSINFO, and PATHCONF.

## Read/Write/Commit pgio Hooks
- `nfs3_read_done()`
  - Handles optional pgio callback, Jukebox retry, records `read_hdrsize`, triggers localio re-probe on successful I/O, invalidates atime, and refreshes inode attrs.
- `nfs3_proc_read_setup()` selects READ proc and cached read header size.
- `nfs3_write_done()` handles callback/Jukebox, updates inode writeback state, and triggers localio re-probe.
- `nfs3_proc_write_setup()` selects WRITE proc.
- `nfs3_commit_done()` handles callback/Jukebox and refreshes inode attrs.
- `nfs3_proc_commit_setup()` selects COMMIT proc.

## LOCALIO Re-Probing
- Under `CONFIG_NFS_LOCALIO`, module parameter `nfs3_localio_probe_throttle` controls periodic LOCALIO probe attempts after normal successful I/O.
- Intended for cases where LOCALIO was disabled after server restart and may later become possible again.

## Locking
- Integrates with lockd through `nlmclnt_operations`.
- For close unlocks, takes and releases NFS lock/open contexts and waits for async I/O counters before unlock where needed.
- `nfs3_proc_lock()` dispatches to `nlmclnt_proc()`.

## Operation Tables
- Defines NFSv3 directory and file inode operations, including ACL hooks when configured.
- `nfs_v3_clientops` wires all v3 implementations into the generic NFS client:
  - metadata ops, lookup/access/readlink/create/remove/rename/link/symlink/mkdir/rmdir/readdir/mknod
  - statfs/fsinfo/pathconf
  - pgio read/write/commit hooks
  - lock, ACL cache clearing, delegation stubs, client/server creation and cloning.

## Research Notes
This file is the main NFSv3 behavior layer above XDR. It coordinates RPC calls, inode cache updates, ACL semantics, retry behavior, writeback completion, lockd, and localio probing.
