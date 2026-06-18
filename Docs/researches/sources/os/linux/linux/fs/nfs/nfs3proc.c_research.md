# File Research: sources/os/linux/linux/fs/nfs/nfs3proc.c

## Purpose
Implements client-side NFSv3 procedure stubs and exports the `nfs_v3_clientops` operation table used by the generic NFS client.

## Core RPC Behavior
- Wraps synchronous RPC calls to retry `-EJUKEBOX` with killable/freezable sleep.
- Provides async jukebox handling for unlink, rename, read, write, and commit completion.
- Implements GETROOT/FSINFO fallback from per-server client to base client when needed.
- Implements NFSv3 procedures: getattr, setattr, lookup/lookupp, access, readlink, create, remove/unlink, rename, link, symlink, mkdir, rmdir, readdir/readdirplus, mknod, statfs, fsinfo, pathconf, read/write setup/done, commit setup/done, and lock handling.

## Creation and Metadata
- Shared `nfs3_createdata` supports create, mkdir, symlink, and mknod.
- Exclusive create falls back from EXCLUSIVE to GUARDED to UNCHECKED on `-ENOTSUPP`.
- POSIX ACLs are created and applied after create/mkdir/mknod when enabled.
- Attribute refreshes use post-op or weak-cache-consistency fattrs.

## I/O and LOCALIO
- Read completion records server read header size, refreshes inode attrs, invalidates atime, and can trigger throttled NFSv3 LOCALIO reprobes.
- Write completion updates inode writeback state and can trigger LOCALIO reprobes.
- `nfs3_localio_probe_throttle` controls periodic LOCALIO reprobe frequency for successful normal RPC I/O.

## Locking
Uses lockd via `nlmclnt_proc()`. Close-unlock paths hold NFS open/lock contexts and can wait for asynchronous I/O counters before unlock.

## Operation Tables
- Directory and file inode operations include permission/getattr/setattr and `fileattr_get = nfs_fileattr_get`.
- ACL hooks are included when `CONFIG_NFS_V3_ACL` is enabled.
- `nfs_v3_clientops` binds all NFSv3 client operations, inode/file ops, lock ops, pgio callbacks, commit callbacks, server creation/cloning, delegation stubs, and close-context behavior.

## Research Notes
This is the main NFSv3 behavioral dispatch file. The important risks are error retry semantics, post-op attribute consistency, create fallback behavior, ACL post-processing, localio reprobe throttling, and preserving callback contracts for async RPC paths.
