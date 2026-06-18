# sources/user-network-fs/libnfs/lib/nfs_v4.c

## Purpose

`sources/user-network-fs/libnfs/lib/nfs_v4.c` implements the high-level asynchronous NFSv4 client operations for libnfs. It turns POSIX-like file API calls into NFSv4 COMPOUND requests, handles path normalization and symlink resolution, parses NFSv4 attributes into libnfs/stat structures, and maintains open, lock, directory, offset, and mount state. The source was read as a complete 5408-line file for this report.

## Important APIs, Types, and Functions

Core callback and request state is carried by `struct nfs4_cb_data`, which stores the `nfs_context`, callback, private data, resolved path, continuation callbacks, open owner, flags, path lookup filler, symlink lookup state, and read/write offset update data. `struct lookup_filler` lets path lookup append operation-specific NFSv4 ops after the common `PUTROOTFH` or `PUTFH`, `LOOKUP...`, and `GETATTR` prefix. `struct nfs4_blob` stores caller-owned or helper-owned variable buffers with optional destructors.

Public async entry points include `nfs4_mount_async`, `nfs4_chdir_async`, `nfs4_stat64_async`, `nfs4_fstat64_async`, `nfs4_open_async`, `nfs4_creat_async`, `nfs4_close_async`, `nfs4_pread_async_internal`, `nfs4_preadv_async_internal`, `nfs4_write_async`, `nfs4_pwrite_async_internal`, `nfs4_fsync_async`, `nfs4_truncate_async`, `nfs4_ftruncate_async`, `nfs4_lseek_async`, `nfs4_opendir_async`, `nfs4_readlink_async`, `nfs4_symlink_async`, `nfs4_link_async`, `nfs4_rename_async`, `nfs4_unlink_async`, `nfs4_rmdir_async`, `nfs4_mkdir2_async`, `nfs4_mknod_async`, `nfs4_getacl_async`, `nfs4_access_async`, `nfs4_access2_async`, `nfs4_chmod_async_internal`, `nfs4_fchmod_async`, `nfs4_chown_async_internal`, `nfs4_fchown_async`, `nfs4_utime_async`, `nfs4_utimes_async_internal`, `nfs4_lockf_async`, and `nfs4_fcntl_async`.

Important operation builders include `nfs4_op_putrootfh`, `nfs4_op_putfh`, `nfs4_op_lookup`, `nfs4_op_getattr`, `nfs4_op_getfh`, `nfs4_op_open_confirm`, `nfs4_op_close`, `nfs4_op_commit`, `nfs4_op_access`, `nfs4_op_create`, `nfs4_op_remove`, `nfs4_op_rename`, `nfs4_op_link`, `nfs4_op_read`, `nfs4_op_write`, `nfs4_op_readdir`, `nfs4_op_truncate`, `nfs4_op_chmod`, `nfs4_op_chown`, `nfs4_op_utimes`, `nfs4_op_lock`, `nfs4_op_locku`, and `nfs4_op_lockt`. Parsing helpers include `nfs_parse_attributes`, `nfs_parse_rwmax`, `nfs_parse_statvfs`, `nfs_parse_statvfs64`, `nfs_get_ugid`, and endian helpers `nfs_hton64`, `nfs_ntoh64`, and `nfs_pntoh64`.

## Control Flow

Most path-based operations allocate `nfs4_cb_data`, resolve the caller path with `nfs4_resolve_path`, optionally split the final component with `data_split_path`, configure `filler.func` and `filler.max_op`, then call `nfs4_lookup_path_async`. That common lookup path builds a COMPOUND request in `nfs4_allocate_op`, queues it through `rpc_nfs4_compound_task`, and routes the result through `nfs4_lookup_path_1_cb`. Successful lookup invokes the operation-specific continuation callback; `NFS4ERR_SYMLINK` or final symlink detection triggers a `READLINK` compound and retries with a rewritten path.

Mount flow is a multi-step chain: connect to port 2049 or configured port, send `SETCLIENTID`, send `SETCLIENTID_CONFIRM`, lookup the export and capture its root filehandle, fetch `FATTR4_MAXREAD` and `FATTR4_MAXWRITE`, then restore the runtime resiliency settings selected by mount options. This stores `server`, `export`, `clientid`, `setclientid_confirm`, root filehandle, and read/write max values in `nfs->nfsi`.

Open flow performs access check, `OPEN`, and `GETFH` as a compound after parent lookup. `nfs4_open_cb` verifies supported access, allocates `struct nfsfh`, copies the returned filehandle and stateid, initializes open seqid and flags such as sync, append, and readonly, and optionally performs `OPEN_CONFIRM`. `O_TRUNC` and `O_EXCL` install continuation callbacks that issue follow-up `SETATTR` requests for size or mode. A final-component symlink returned by `OPEN` is retried through `nfs4_open_readlink` unless `O_NOFOLLOW` is set.

Read and write flow uses direct filehandles rather than path lookup. `nfs4_pread_async_internal` and `nfs4_preadv_async_internal` send `PUTFH` plus `READ` using zero-copy aware RPC read helpers; callbacks update `nfsfh->offset` when requested. `nfs4_write_async` either writes at the current offset or, for append handles, first fetches current size through `GETATTR`, then writes at EOF. Non-sync writes mark `fh->is_dirty`, and `nfs4_close_async` includes `COMMIT` before `CLOSE` when dirty.

Directory flow opens with lookup plus `GETFH` and `READDIR`. `nfs4_parse_readdir` converts linked `entry4` results to libnfs `nfsdirent` entries, records cookies, and repeats `READDIR` via `nfs4_opendir_continue` until EOF. Link and rename are two-phase flows that capture one parent or source filehandle, then switch `data->path` and `filler.data` to complete `LINK` or `RENAME` with `SAVEFH` and `PUTFH`.

## State and Persistence Behavior

The file has no file-backed persistence, but it mutates durable client-session and handle state. `nfs->nfsi` stores server/export strings, current working directory, NFSv4 root filehandle, client id, verifier, read/write limits, open owner counter, and lock owner state. `struct nfsfh` instances retain NFS filehandles, stateids, open and lock seqids, current offset, append/sync/readonly flags, and dirty-write status across async calls.

Transient state is owned by `nfs4_cb_data` and released by `free_nfs4_cb_data`, including path strings, filler data, and up to four blobs. Some callbacks intentionally transfer ownership by nulling a blob before invoking the application callback, for example returning an opened `nfsfh`, `nfsdir`, or readlink target. With multithreading enabled, open/close/truncate paths serialize around `nfs4_open_call_mutex`, and open owner allocation uses `nfs4_open_counter_mutex`.

## Dependencies and Integration Points

Direct dependencies include generated NFSv4 ZDR types from `libnfs-raw-nfs4.h`, RPC task wrappers from `libnfs-raw.h`, public and private libnfs context definitions from `libnfs.h` and `libnfs-private.h`, linked-list helpers, platform compatibility headers, and system headers for stat, statvfs, utime, passwd lookup, major/minor device extraction, and networking. It integrates upward with the libnfs async API and downward with `rpc_nfs4_compound_task`, `rpc_nfs4_compound_task2`, `rpc_nfs4_read_task`, `rpc_nfs4_readv_task`, and `rpc_nfs4_write_task`.

The attribute masks `standard_attributes`, `statvfs_attributes`, `getacl_attributes`, and `rwmax_attributes` define the NFSv4 attribute ordering assumed by the local parsers. This makes the operation builders and parsers tightly coupled: changing masks or server result order assumptions requires updating the corresponding decode routines.

## Risks and Edge Cases

The path lookup and symlink retry logic mutates path buffers in place and depends on correct ownership transfers between `path`, `filler.data`, and blobs. Bugs here can cause leaks, double frees, incorrect final-component handling, or infinite symlink retries if normalization does not collapse the rewritten path as expected. `LOOKUP_FLAG_NO_FOLLOW` and `O_NOFOLLOW` are handled in separate stat/readlink and open paths, so regressions can diverge between `lstat`-style calls and `open`.

Attribute parsing is position-based against the requested bitmap and uses manual buffer cursor arithmetic. The `CHECK_GETATTR_BUF_SPACE` macro catches short buffers, but parser correctness still depends on exact NFSv4 attribute order and byte order. UID/GID strings are converted either numerically or through `getpwnam`; nonnumeric names without passwd support become 65534.

NFSv4 state sequencing is fragile. `nfs_increment_seqid` intentionally skips increment for selected protocol errors, while open, close, lock, unlock, and confirm callbacks update different stateids. Retry, reconnect, or callback ordering bugs can leave the server and client with different seqid expectations. Dirty writes rely on close or fsync issuing `COMMIT`; an application that never closes or syncs a handle after unstable writes can leave server-side persistence dependent on server behavior.

There are several small implementation hazards: some allocation failures return `0` rather than `-1` in `nfs4_mknod_async`; `nfs4_populate_symlink` has an unreachable `return 1`; statvfs ignores its `path` argument and always queries the mounted root filehandle; append writes race with other clients because EOF is fetched before write; directory entries are pushed to the head, so returned order is reverse of server traversal; and several callbacks pass stack-local result structs to the application callback, so callbacks must consume synchronously as expected by libnfs conventions.

## Test Signals

Useful coverage includes mount handshake tests against NFSv4 servers with and without `OPEN_CONFIRM`; path normalization and symlink tests for intermediate symlinks, final symlinks, `NO_FOLLOW`, `O_NOFOLLOW`, relative paths, root paths, and split final components; stat/fstat/statvfs tests validating all parsed fields and short-attribute error handling; open/create/truncate/exclusive-mode tests that inspect server-side mode, size, stateid, and seqid behavior; read/write tests for offset updates, append behavior, sync versus unstable write plus commit, zero-length reads/writes, and server max read/write limits; directory tests spanning multi-page `READDIR` and EOF; rename/link tests across directories; lock and fcntl tests for `SEEK_SET`, `SEEK_CUR`, `SEEK_END`, lock owner reuse, unlock stateid updates, and conflict cases; and sanitizer or fault-injection runs around allocation failures and callback cancellation/timeouts.
