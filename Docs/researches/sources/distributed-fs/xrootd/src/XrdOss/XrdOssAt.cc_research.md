# sources/distributed-fs/xrootd/src/XrdOss/XrdOssAt.cc

## Purpose

`XrdOssAt.cc` implements directory-relative OSS operations using POSIX `*at()` syscalls. It supports opening relative files/directories, stat, unlink, and remove-directory against an already open OSS directory object.

## Important APIs, Types, and Functions

Implemented `XrdOssAt` methods are `Opendir`, `OpenRO`, `Remdir`, `Stat`, and `Unlink`. Local macros `BOILER_PLATE` validate that the anchor object is a directory, the path is relative, and the directory FD is available; `OPEN_AT` opens with close-on-exec handling. Local RAII `openHelper` closes untransferred FDs.

## Control Flow

Each method validates the anchor and relative path. `Opendir()` opens the target with `openat`, wraps it in `fdopendir`, and returns an `XrdOssDir`. `OpenRO()` returns an `XrdOssFile` around an `openat` FD. `Remdir()` calls `unlinkat(..., AT_REMOVEDIR)`. `Stat()` calls `fstatat` and optionally maps device info through `XrdOssCache::DevInfo`. `Unlink()` refuses directories, deletes regular files directly with cache adjustment, or follows symlink targets to remove the underlying cache data and then the symlink.

## State and Persistence Behavior

Operations mutate only the online local filesystem view relative to the directory FD. Returned file/dir objects own transferred FDs. `Unlink()` updates cache accounting by device or cache base path depending on symlink target naming.

## Dependencies and Integration Points

The implementation depends on `XrdOssDF`, default `XrdOssDir`/`XrdOssFile`, `XrdOssCache`, `XrdOssPath`, `XrdSysFD`, and POSIX `openat`, `fstatat`, `unlinkat`, and `readlinkat`. It is unavailable when `HAVE_FSTATAT` is not defined.

## Risks and Edge Cases

Absolute paths and missing directory FDs are rejected, preventing unintended name-to-name translation. Symlink target deletion is sensitive: failure to unlink an existing target is logged and returned. One error path returns `-retc` after `retc` is already negative, which would flip the sign and should be reviewed. Cache adjustment depends on the target path's `xChar` suffix convention.

## Test Signals

Tests should cover unsupported builds, non-directory anchors, absolute path rejection, opened FD transfer, close-on-exec behavior, stat with device info, regular-file unlink cache adjustment, symlink target unlink, missing symlink target, directory unlink rejection, and sign of symlink-target unlink errors.
