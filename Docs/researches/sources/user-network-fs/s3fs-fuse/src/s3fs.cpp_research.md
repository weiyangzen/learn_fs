# sources/user-network-fs/s3fs-fuse/src/s3fs.cpp

## Purpose

This file is the main executable and FUSE operation implementation for `s3fs`, a filesystem that projects an S3 bucket or bucket prefix as a POSIX-like filesystem. It owns the command-line parser, process initialization, the `fuse_operations` table, service/bucket validation, and almost every high-level filesystem operation: attribute lookup, directory creation/removal/listing, object creation/deletion/rename, symlink handling, chmod/chown/utimens, truncate/open/read/write/flush/fsync/release, statfs, access checks, and optional extended attributes.

The implementation translates filesystem state into S3 objects plus S3 user metadata. Object bodies store regular file data and symlink targets; metadata headers store POSIX-ish fields such as uid, gid, mode, atime, mtime, ctime, content type, and optional xattrs. It relies heavily on stat and file caches to mask S3 latency and to preserve local semantics for files that are open, dirty, or not yet uploaded.

## Important APIs, Types, and Functions

The public surface in this file is mostly the `main()` function plus a few non-static helpers used by other compilation units:

- `main(int argc, char* argv[])`: initializes XML, SSL, curl, credentials, options, cache/disk policy, FUSE operation callbacks, enters `fuse_main`, then destroys curl/SSL/XML state.
- `put_headers(const char* path, const headers_t& meta, bool is_copy, bool use_st_size)`: updates object metadata through copy-style PUT header requests, switching to multipart metadata copy for large objects.
- `get_object_sse_type(const char* path, sse_type_t& ssetype, std::string& ssevalue)`: reads object metadata and reports SSE-S3, SSE-KMS, SSE-C, or disabled state.

Most implementation functions are static FUSE callbacks or helpers:

- Metadata and access: `get_object_attribute`, `chk_dir_object_type`, `remove_old_type_dir`, `check_object_access`, `check_object_owner`, `check_parent_object_access`.
- Object creation/removal: `create_file_object`, `s3fs_mknod`, `s3fs_create`, `create_directory_object`, `s3fs_mkdir`, `s3fs_unlink`, `s3fs_rmdir`, `directory_empty`.
- Rename/copy: `rename_object`, `rename_object_nocopy`, `rename_large_object`, `clone_directory_object`, `rename_directory`, `s3fs_rename`.
- Metadata mutation: `s3fs_chmod`, `s3fs_chmod_nocopy`, `s3fs_chown`, `s3fs_chown_nocopy`, `s3fs_utimens`, `s3fs_utimens_nocopy`, `update_mctime_parent_directory`.
- Data path: `s3fs_truncate`, `s3fs_open`, `s3fs_read`, `s3fs_write`, `s3fs_flush`, `s3fs_fsync`, `s3fs_release`.
- Directories: `s3fs_opendir`, `s3fs_readdir`, `readdir_multi_head`, `list_bucket`, `remote_mountpath_exists`.
- Xattrs: `get_meta_xattr_value`, `get_parent_meta_xattr_value`, `get_xattr_posix_key_value`, `build_inherited_xattr_value`, `build_xattrs`, `set_xattrs_to_header`, `s3fs_setxattr`, `s3fs_getxattr`, `s3fs_listxattr`, `s3fs_removexattr`.
- Startup and options: `s3fs_init`, `s3fs_destroy`, `s3fs_check_service`, `set_mountpoint_attribute`, `set_bucket`, `parse_bucket_size`, `my_fuse_opt_proc`.

Important local state includes mountpoint uid/gid/mode/umask, FUSE uid/gid/umask overrides, `mountpoint`, `nocopyapi`, `norenameapi`, `support_compat_dir`, multipart thresholds, `singlepart_copy_limit`, `max_dirty_data`, `fake_diskfree_size`, `update_parent_dir_stat`, `bucket_block_count`, `s3fs_block_size`, and atomic `has_mp_stat`.

## Control Flow

Startup begins in `main()`. It initializes libxml and platform sysconf data, configures the credential object on `S3fsCurl`, parses top-level long options, loads SSE environment settings, initializes SSL and curl, then lets `fuse_opt_parse` call `my_fuse_opt_proc` for s3fs-specific `-o` options and non-option bucket/mountpoint arguments. After option validation, it checks credential consistency, mountpoint presence, temp/cache directories, disk-space policy, utility mode, and multipart/cache mode interactions. It then fills `struct fuse_operations`; xattr callbacks are only registered when `use_xattr` is enabled, and chmod/chown/utimens choose copy or nocopy implementations based on `nocopyapi`.

FUSE initialization calls `s3fs_init()`, which optionally removes cache directories, initializes the thread pool, loads IAM role metadata, validates bucket access through `s3fs_check_service()`, enables atomic truncation where available, and installs signal handling. `s3fs_check_service()` issues a service check and handles region mismatch, invalid credentials, permanent redirect, and invalid SSE argument responses with targeted retry or fatal messages.

Attribute lookup centers on `get_object_attribute()`. It normalizes mountpoint cases, recognizes directory encodings (`dir/`, `dir`, `dir_$folder$`, and implicit directories with only children), checks `StatCache`, sends HEAD requests, performs compatible-directory overchecks only after `-ENOENT`, optionally does list checks through `directory_empty`, converts headers into `struct stat`, and writes positive or negative cache entries. Permission checks layer on top of this metadata with FUSE context uid/gid and configured uid/gid/umask overrides.

Object mutation generally follows S3 constraints. Creating files or directories builds metadata headers and either creates an empty object or creates an open dirty `FdEntity` that is uploaded later. Metadata-only changes normally use `x-amz-copy-source` with `x-amz-metadata-directive: REPLACE`; when copy APIs are disabled, they load the whole object through `FdEntity`, mutate local metadata, and flush/reupload. Large copies route through multipart copy. Directory changes may rebuild legacy directory objects into normalized `dir/` objects.

The file data path is cache-backed. `s3fs_open()` resolves permissions and metadata, pins stat cache with the no-truncate flag, opens an `FdEntity`, and handles `O_TRUNC`. `s3fs_read()` and `s3fs_write()` operate on an existing pseudo fd from `fi->fh`; writes update ctime/mtime and may trigger `RowFlush()` when `BytesModified()` exceeds `max_dirty_data`, then punch holes to reclaim cache disk space. `flush`, `fsync`, and `release` coordinate content upload, pending metadata upload, stat cache updates, and parent directory timestamp updates.

Directory listing uses `list_bucket()` to issue ListObjects v1/v2 requests with delimiter/prefix/max-keys parameters, parse XML with libxml, append objects into `S3ObjList`, and follow continuation tokens or markers. `s3fs_readdir()` fills `.` and `..`, then `readdir_multi_head()` issues batched HEAD requests through `multi_head_request` and `ThreadPoolMan`-backed machinery to populate stat data for entries. It also merges entries that exist only in `StatCache`, covering newly created but not yet uploaded files.

## State and Persistence Behavior

Persistent filesystem state is stored in S3 object bodies and headers. Regular file contents are object bodies; symlink targets are stored as object bodies with symlink mode metadata; directories are represented as zero-length directory objects, usually normalized to keys ending with `/`. POSIX attributes live in `x-amz-meta-*` headers: uid, gid, mode, atime, ctime, mtime, xattr, and content type.

In-memory and local state is equally important. `StatCache` stores positive stats, negative entries, xattr/symlink data, directory object lists, and no-truncate entries for open/new files. `FdManager`, `FdEntity`, and `AutoFdEntity` manage local temporary or cache files, pseudo fds, dirty page tracking, multipart upload state, pending metadata, and cache file renames/deletes. Startup options control cache deletion, cache directory use, disk-space guarantees, multipart thresholds, thread counts, and xattr registration.

The file explicitly handles S3's lack of atomic POSIX operations. Rename copies to the destination then deletes the source. Directory rename enumerates all children, creates destination directories first, copies files, then removes old directories bottom-up. Chmod/chown/utimens and xattr changes are metadata replacement copies unless `nocopyapi` forces a full object reload/reupload. Parent directory timestamps are optional and disabled unless `update_parent_dir_stat` is set.

## Dependencies and Integration Points

This file integrates with FUSE/libfuse, curl/S3 wrappers, credential handling, metadata conversion, fd/cache management, S3 listing/XML parsing, multipart utilities, thread requests, logging, signal handling, and auth/SSL lifecycle. The key local includes are `s3fs.h`, `metaheader.h`, `fdcache*.h`, `curl*.h`, `s3objlist.h`, `s3fs_xml.h`, `s3fs_auth.h`, `s3fs_cred.h`, `s3fs_threadreqs.h`, `mpu_util.h`, and `threadpoolman.h`.

The code also depends on many global configuration variables declared elsewhere, such as `mount_prefix`, `region`, `s3host`, `service_path`, `pathrequeststyle`, `nomultipart`, `noxmlns`, `foreground`, `utility_mode`, request counters, and logging flags.

## Risks and Edge Cases

The highest-risk area is the semantic mismatch between POSIX and S3. Rename and metadata updates are non-atomic copy/delete sequences. A failure after destination copy but before source delete can leave duplicates; a failure during directory rename can leave a partially copied tree. Concurrent writers across processes or hosts can observe stale stat/list cache or overwrite metadata with copy-replace operations.

The stat path is intentionally complex and should be regression-tested carefully. It handles mountpoint stat objects, bucket-root `//` special cases, negative cache, compatible directory suffixes, implicit directories, and backend quirks where HEAD on `dir` succeeds when only `dir/` exists. The code explicitly avoids compatible-directory overchecks after transient non-ENOENT errors to avoid recreating objects during temporary failures.

Open-file state is delicate. Newly created files may exist only in no-truncate stat cache until flush/release uploads them. Metadata mutations on open files merge into `FdEntity` pending metadata, so bugs in `MergeOrgMeta`, `UploadPending`, or stat cache refresh can expose stale attributes. FUSE can call `release` without prior `flush`, so `release` has to upload modified content defensively.

`parse_bucket_size()` appears fragile: the digit-validation loop uses `for(size_t i = 0; i < pos; ++i)`, but `pos` is not initialized when no unit suffix is present. That deserves focused review or tests because `bucket_size=12345` without a suffix may exercise undefined or unintended behavior.

## Test Signals

Useful tests should cover stat lookup on all directory encodings, file create/open/write/read/flush/release, truncate and `O_TRUNC`, cache invalidation, regular and directory rename with injected failures, metadata mutations in normal and `nocopyapi` modes, xattr/ACL inheritance, service-check error handling, and option parsing for SSE, credentials, cache/disk policy, bucket prefix syntax, and `bucket_size`.
