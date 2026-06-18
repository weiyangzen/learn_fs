# File Research: sources/os/linux/linux-stable/fs/smb/client/inode.c

Read status: complete.

## Purpose

Implements CIFS/SMB inode lifecycle, metadata conversion, attribute revalidation, VFS mutation operations, and setattr/truncate handling. This is the SMB client’s main bridge between server metadata and Linux VFS inode state.

## Main Responsibilities

- Convert SMB1 Unix, SMB2/SMB3 all-info, and SMB3.1.1 POSIX metadata into `struct cifs_fattr`.
- Instantiate and refresh Linux inodes from `cifs_fattr`, including inode operations, file operations, address-space operations, size, timestamps, ownership, mode, reparse tags, and symlink targets.
- Decide when cached inode data and pagecache mappings must be invalidated.
- Fetch inode metadata by path or by open file handle, with dialect-specific paths for legacy Unix extensions, SMB2/3, POSIX extensions, ACL-derived modes, SFU emulation, MF symlinks, DFS junctions, and reparse points.
- Implement VFS operations for unlink, mkdir, rmdir, rename, getattr, fiemap, truncate, chmod/chown/chgrp/time updates, and root inode lookup.
- Handle server inode-number collisions and automatically disable `serverino` when the server provides unstable or unusable inode numbers.

## Important Functions

- `cifs_set_netfs_context()` / `cifs_set_ops()`
  - Initialize netfs state and choose inode/file/address-space operations based on file type and mount flags.
  - Regular files select direct, strict, no-BRL, or normal CIFS file ops; directories select namespace ops when automounting; symlinks select symlink ops.

- `cifs_revalidate_cache()`
  - Compares new metadata with cached mtime and remote size.
  - Marks the mapping invalid and invalidates fscache when data may have changed and no read oplock protects the cache.

- `cifs_fattr_to_inode()`
  - Central conversion from SMB client metadata to Linux inode fields.
  - Rejects type changes with `-ESTALE`, preserves local mode under `dynperm`, updates delete-pending state, handles safe size updates, transfers symlink targets, and initializes new inodes.

- `cifs_unix_basic_to_fattr()`
  - Converts legacy `FILE_UNIX_BASIC_INFO` into Linux mode, dtype, device numbers, uid/gid, size, timestamps, unique id, and link count.

- `cifs_sfu_type()` / `cifs_sfu_mode()`
  - Interpret SFU/Services-for-Unix emulated special files and SETFILEBITS xattrs.
  - Recognize block/char devices, sockets, FIFOs, and SFU symlink payloads.

- `smb311_posix_info_to_fattr()` / `cifs_open_info_to_fattr()`
  - Convert SMB3 POSIX query data or standard SMB open/query information into `cifs_fattr`.
  - Account for timezone adjustment, readonly mode masking, reparse-point conversion, symlink targets, link counts, and POSIX SID-to-id mapping.

- `cifs_get_fattr()` / `smb311_posix_get_fattr()`
  - Fetch path metadata, handle DFS/junction cases, reparse points, backup-credential fallback, server inode numbers, ACL mode/ownership extraction, SFU/MF symlink tweaks, and readonly permission masking.

- `cifs_get_inode_info()` / `smb311_posix_get_inode_info()` / `cifs_get_inode_info_unix()`
  - Public inode metadata refresh paths for non-POSIX SMB, SMB3 POSIX extensions, and legacy Unix extensions.

- `cifs_iget()` / `cifs_root_iget()`
  - Find or allocate inodes with `iget5_locked()`, using unique id plus create time as identity.
  - Handle directory inode collisions, root prepaths, DFS junction root metadata, and IPC fake roots.

- `__cifs_unlink()` / `cifs_unlink()`
  - Implements file deletion with dentry unhashing, deferred-close flushing, POSIX delete fallback, standard unlink, SMB2 sillyrename behavior, pending-delete rename fallback, readonly attribute clearing, and parent/child cache invalidation.

- `cifs_mkdir()` / `cifs_mkdir_qinfo()` / `cifs_posix_mkdir()`
  - Create directories through SMB3 POSIX, legacy POSIX, or generic mkdir.
  - Query new inode information afterward and apply mode, setgid, dynperm, and setuid/setgid mount behavior.

- `cifs_rmdir()`
  - Removes directories, marks deleted inodes pending-delete, clears size/link count, and invalidates parent and child metadata.

- `cifs_rename2()` / `cifs_do_rename()`
  - Implements VFS rename with path-based SMB rename, legacy open-file rename fallback, target dentry unhashing, deferred-close handling, no-replace support, target unlink/rmdir fallback, and directory delete-pending updates.

- `cifs_dentry_needs_reval()`
  - Decides whether inode attributes must be refreshed based on delete-pending/tmpfile state, oplocks, lookup cache state, cached directory freshness, `acdirmax`/`acregmax`, and noserverino hardlinks.

- `cifs_revalidate_mapping()` / `cifs_zap_mapping()`
  - Serializes pagecache invalidation with `CIFS_INO_LOCK`.
  - Skips invalidation for swapfiles and `cache=singleclient`.

- `cifs_getattr()`
  - Implements stat/statx behavior, waits for dirty pages when size/times/blocks are requested, optionally forces sync, fills birth time and compressed/encrypted statx attributes, and adjusts ownership for multiuser mounts without Unix/ACL ownership.

- `cifs_fiemap()`
  - Flush-waits dirty data, finds a readable handle, and dispatches to dialect-specific fiemap support.

- `cifs_file_set_size()` / `cifs_setsize()`
  - Prefer handle-based EOF setting, fall back to path-based size setting, resize netfs/fscache/pagecache, and update local inode block estimates.

- `cifs_setattr_unix()` / `cifs_setattr_nounix()` / `cifs_setattr()`
  - Implement chmod/chown/chgrp/truncate/timestamp updates through legacy Unix info, ACL security descriptors, SMB3 POSIX ACL path, DOS readonly attributes, or generic file-info setting.
  - Avoids setting ctime/mtime on `ATTR_OPEN` and after ftruncate paths that would disable server automatic timestamp updates.

## Dependencies

- Uses CIFS core structures from `cifsglob.h`, mount state from `cifs_fs_sb.h` and `fs_context.h`, dialect operations from `cifsproto.h` and `smb2proto.h`, cached directory helpers, ACL helpers, reparse helpers, fscache, and netfs APIs.
- Relies heavily on `server->ops` indirection for dialect-specific open/query/setinfo/delete/rename/ACL/reparse/fiemap behavior.

## Notable Behaviors

- Inode identity is not just server file id; create time is also compared to reduce stale aliasing.
- Reparse points are treated conservatively. Unsupported name-surrogate directory reparse points can become junction automount placeholders.
- If a server returns unusable inode numbers, the mount can automatically switch away from `serverino`.
- Many paths mark `CIFS_I(inode)->time = 0` rather than immediately querying, forcing later revalidation.
- Delete and rename paths actively close deferred handles to avoid server-side sharing conflicts.
- ACL-enabled mounts may intentionally re-query after readdir so mode and ownership visible to `ls -l` are not stale or placeholder values.
