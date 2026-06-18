# sources/user-network-fs/libnfs/lib/nfs_v3.c

## Purpose

`nfs_v3.c` is the high-level asynchronous NFSv3 backend for libnfs. It adapts the public libnfs async file API to raw MOUNTv3, NFSv3, and NFSACL RPC tasks: mounting and unmounting exports, resolving paths to file handles, opening/creating files, reading and writing file data, directory enumeration, metadata/stat operations, access checks, links, renames, removals, mkdir/rmdir/mknod, truncate, fsync/commit, chdir, and ACL retrieval.

The file is not a standalone public facade. `lib/libnfs.c` dispatches generic APIs such as `nfs_mount_async`, `nfs_open_async`, `nfs_pread_async`, `nfs_write_async`, `nfs_opendir_async`, `nfs_access_async`, `nfs_rename_async`, and others to these `nfs3_*` implementations when `nfs->nfsi->version == NFS_V3`. Build integration includes this source through `lib/CMakeLists.txt` and `lib/Makefile.am`.

## Important APIs, Types, and Helpers

Primary externally used functions in this file include:

- `nfs3_mount_async` / `nfs3_umount_async`: connect to mountd, obtain or release the export file handle, discover nested mounts when enabled, connect to NFSd, negotiate transfer sizing through FSINFO, and restore RPC resiliency settings after mount.
- `nfs3_open_async`, `nfs3_creat_async`, `nfs3_close_async`: implement NFSv3 open semantics using LOOKUP, ACCESS, optional CREATE, optional SETATTR truncation, and local `struct nfsfh` state because NFSv3 has no server-side open/close state.
- `nfs3_pread_async_internal`, `nfs3_preadv_async_internal`, `nfs3_write_async`, `nfs3_pwrite_async_internal`: implement data transfer around READ/WRITE RPCs with negotiated `readmax`/`writemax`, handle append by GETATTR, update local offsets when requested, and track dirty/sync state for COMMIT-on-close behavior.
- `nfs3_opendir_async`: reads directories through READDIRPLUS when supported, falls back to READDIR plus LOOKUP-based attribute completion, and uses libnfs directory cache integration.
- Metadata and namespace functions: `nfs3_stat_async`, `nfs3_stat64_async`, `nfs3_fstat_async`, `nfs3_fstat64_async`, `nfs3_statvfs_async`, `nfs3_statvfs64_async`, `nfs3_readlink_async`, `nfs3_chmod_async_internal`, `nfs3_fchmod_async`, `nfs3_chown_async_internal`, `nfs3_fchown_async`, `nfs3_utimes_async_internal`, `nfs3_utime_async`, `nfs3_truncate_async`, `nfs3_ftruncate_async`, `nfs3_fsync_async`, and `nfs3_getacl_async`.
- Namespace mutation functions: `nfs3_link_async`, `nfs3_rename_async`, `nfs3_symlink_async`, `nfs3_mkdir2_async`, `nfs3_rmdir_async`, `nfs3_unlink_async`, and `nfs3_mknod_async`.

Important local continuation payloads include `struct nfs_mcb_data` for multi-call writes, `struct nfs_link_data`, `struct nfs_rename_data`, `struct nfs_symlink_data`, `struct nfs_chown_data`, `struct mknod_cb_data`, `struct open_cb_data`, `struct rdpe_cb_data`, and mount discovery structs. They are threaded through `struct nfs_cb_data` from `libnfs.c`, whose cleanup releases `continue_data` through `free_continue_data`, `saved_path`, copied file handles, and buffers.

Key helper routines:

- `check_nfs3_error` translates RPC transport statuses into callback errors for error, cancel, and timeout.
- `nfs3_lookuppath_async` and `nfs3_lookup_path_async_internal` normalize relative/absolute paths, traverse components, follow symlinks under `MAX_LINK_COUNT`, honor `O_NOFOLLOW`/`no_follow`, switch to nested mount file handles, and finish by invoking a continuation with a resolved file handle.
- `fattr3_to_nfs_attr` and `specdata3_to_rdev` convert raw protocol attributes to libnfs-visible attribute/stat fields.
- `nfs3_fill_WRITE3args` and `nfs3_fill_READ3args` centralize raw READ/WRITE argument construction.

## Control Flow

Most operations follow the same asynchronous pipeline:

1. Allocate and initialize `struct nfs_cb_data` plus optional operation-specific continuation data.
2. Resolve a path with `nfs3_lookuppath_async` unless the API already has a `struct nfsfh`.
3. In a continuation, populate an NFSv3 RPC args struct with the resolved file handle or parent directory handle.
4. Schedule a raw RPC task such as `rpc_nfs3_lookup_task`, `rpc_nfs3_getattr_task`, `rpc_nfs3_access_task`, `rpc_nfs3_create_task`, `rpc_nfs3_readdirplus_task`, `rpc_nfs3_write_task`, or `rpc_nfs3_commit_task`.
5. In the raw callback, first check RPC transport status, then translate protocol status through `nfsstat3_to_errno` or `mountstat3_to_errno`.
6. Return either result data or an errno-style failure to the caller callback and free the callback state.

Mounting is a longer state machine: connect to mountd, run MNT for the root export, optionally EXPORT plus MNT for nested child exports, disconnect from mountd, connect to NFSd, issue FSINFO, validate/negotiate read/write/readdir buffer sizes, GETATTR the root handle, optionally GETATTR nested mount handles, and finally invoke the user callback. After mount setup, RPC resiliency is changed from fail-fast mount behavior back to the user-selected reconnect/timeout/retrans settings.

Path lookup is central to almost every path-based API. It mutates `data->saved_path` temporarily to split components, restores separators after scheduling RPCs, follows symlinks by READLINK, converts absolute symlink targets back into export-relative paths only when they remain inside the mounted export, normalizes `..`/`.` components, and restarts lookup from the root or nested mount file handle as needed.

Open is emulated because NFSv3 has no open RPC. The first lookup either succeeds and proceeds to ACCESS, optional truncate, and `struct nfsfh` allocation, or fails with `NOENT` and `O_CREAT`, in which case the code resolves the parent directory and sends CREATE. `O_EXCL` is handled using preexisting lookup failure/success behavior plus guarded CREATE.

Directory reading starts with READDIRPLUS, accumulates entries across cookies until EOF, and falls back to READDIR when the server returns `NFS3ERR_NOTSUPP`. Entries lacking attributes are completed through per-entry LOOKUP calls; nested mount attributes are also synthesized into directory entries when a nested export matches the listed name.

Writes mark the handle dirty, cap request size to `writemax`, send chunk WRITE RPCs, track outstanding calls with `data->num_calls`, reissue partial writes, collect `max_offset`, and update the local file offset only when `update_pos` is set. Reads cap a single NFSv3 READ request to `readmax`; higher-level looping for large reads is handled in `libnfs.c`.

## State and Persistence Behavior

Persistent client-side state updated here lives mostly under `nfs->nfsi`, `nfs->rpc`, `struct nfsfh`, and directory caches:

- Mount stores duplicated `server` and `export` strings, sets `nfs->rpc->server`, fills `nfs->nfsi->rootfh`, discovers and stores `nfs->nfsi->nested_mounts`, and negotiates `readmax`, `writemax`, and readdir buffer sizing.
- `nfs3_chdir_async` replaces `nfs->nfsi->cwd` with the normalized resolved path. It locks `rpc_mutex` when multithreading is enabled.
- `struct nfsfh` stores the file handle, current offset, and local flags: `is_sync`, `is_append`, `is_readonly`, and `is_dirty`. `nfs3_close_async` sends COMMIT through `nfs_fsync_async` only when `is_dirty` is set, then frees the local handle.
- Directory cache is consulted in `nfs3_opendir_continue_internal` and invalidated by mutating operations such as link, rename, symlink, chmod, utimes, mknod, unlink, rmdir, mkdir, truncate/ftruncate, and create.
- No NFSv3 server-side open or lock persistence is established by this file. Durability relies on WRITE stability mode (`FILE_SYNC` when `O_SYNC`, otherwise `UNSTABLE`) and explicit COMMIT on fsync/dirty close.

Callback result memory often points to stack-local converted structs during the callback (`struct stat`, `struct nfs_stat_64`, `struct statvfs`, `struct nfs_statvfs_64`, ACL wrapper), so callers must consume or copy data before returning according to libnfs callback conventions. File handles and directory handles returned to users are heap allocated.

## Dependencies and Integration Points

This implementation depends on generated/raw protocol bindings from `libnfs-raw.h`, `libnfs-raw-mount.h`, and `libnfs-zdr.h`, plus private libnfs definitions from `libnfs-private.h`. It uses raw task functions for MOUNTv3, NFSv3, and NFSACL, RPC context connection/disconnection and resiliency APIs, platform headers for stat/statvfs/utime/device macros, and private helpers such as `nfs_set_error`, `nfs_get_error`, `nfs_get_export`, `nfs_normalize_path`, `nfs_dircache_find`, `nfs_dircache_drop`, `nfs_free_nfsdir`, and `free_nfs_cb_data`.

The main integration path is `lib/libnfs.c`, where generic public async functions switch on `nfs->nfsi->version` and call these NFSv3 functions. `libnfs-sync.c` builds synchronous APIs on top of the generic async layer, so changes here can affect both async and sync NFSv3 users. NFSv4 behavior lives separately in `nfs_v4.c`; shared API contracts must remain compatible across both versions.

## Risks and Edge Cases

- Path parsing relies on mutable duplicated strings, embedded NUL separators, and pointers that sometimes get reassigned to interior storage. Ownership bugs are easy in paths split into parent/object pairs, especially for paths without slashes.
- Symlink resolution rejects absolute targets outside the export and caps recursion, but it restarts path lookup and mutates `saved_path`; regressions could create loops, incorrect export containment checks, or double frees.
- NFSv3 open semantics are only emulated. ACCESS result comparison in `nfs3_open_cb` requires exact equality with the requested access mask rather than accepting a superset, which may deny otherwise sufficient access if a server returns additional bits.
- Write behavior truncates an individual internal write call to `writemax`; large public writes are expected to be split by the generic layer. Any caller bypassing that layer will only write up to the negotiated maximum.
- Multi-call write state uses shared `struct nfs_cb_data` fields and atomics around `num_calls`; concurrent callback ordering and partial-write reissue paths are high-risk for use-after-free or incorrect byte counts.
- Directory enumeration reverses entry order by pushing each entry at the head of the list. Consumers must not assume server order unless higher layers reorder.
- READDIRPLUS fallback performs many LOOKUP calls for missing attributes; this can be slow and can return partial metadata when some lookups fail.
- Several callbacks pass converted stack objects to user callbacks. This is normal for synchronous callback consumption but risky if a caller stores returned pointers.
- Mutation cache invalidation is manual and per-operation; any missing `nfs_dircache_drop` can expose stale directory results.
- Error handling sometimes returns protocol-derived errno values and sometimes hard-coded transport values such as `-ENOMEM`, `-EFAULT`, or `-EINTR`; callers should rely on negative status rather than string parsing.

## Test Signals

Useful tests for this file should exercise the generic libnfs API with `NFS_V3` selected, because public calls dispatch here through `libnfs.c`.

High-value behavioral signals:

- Mount and umount against an NFSv3 server, including explicit `mountport`/`nfsport`, FSINFO negotiation, reconnect/resiliency restoration, and auto traversal of nested exports.
- Path lookup with relative paths, absolute export-contained symlinks, absolute symlinks outside the export, chained symlinks exceeding `MAX_LINK_COUNT`, `readlink` no-follow behavior, and nested mount longest-prefix selection.
- Open/create combinations: read-only open, write open, `O_CREAT`, `O_CREAT|O_EXCL`, `O_TRUNC`, `O_APPEND`, and `O_SYNC`, including existing and missing files.
- Read/write flows around `readmax`/`writemax`, append writes, partial WRITE responses, dirty close COMMIT, explicit fsync, and local offset updates for read/write versus pread/pwrite.
- Directory reads from servers supporting READDIRPLUS and servers returning `NFS3ERR_NOTSUPP`, including missing-attribute LOOKUP fallback and stale cache invalidation after mkdir/unlink/rename/create.
- Metadata conversion for stat/stat64/statvfs/statvfs64, device nodes via mknod and `specdata3_to_rdev`, nanosecond timestamps, chmod/chown/utime no-follow variants, and ACL retrieval.
- Failure paths for RPC cancel, timeout, transport error, protocol errors, allocation failures if fault injection is available, and callbacks that verify `free_nfs_cb_data` releases continuation state exactly once.
