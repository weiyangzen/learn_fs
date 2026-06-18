# sources/distributed-fs/xrootd/src/XrdFfs/XrdFfsPosix.cc

## Purpose

This file provides C ABI wrappers around `XrdPosixXrootd` and higher-level operations that fan out metadata mutations and queries across all known data servers. It is the main bridge between FUSE callbacks and XRootD client/file-system operations.

## Important APIs, Types, and Functions

Simple wrappers include `stat`, `opendir`, `readdir`, `closedir`, `mkdir`, `rmdir`, `open`, `close`, `lseek`, `read`, `pread`, `write`, `pwrite`, `fsync`, `unlink`, `rename`, `ftruncate`, `truncate`, and `getxattr`. `stat()` also converts HPSS block-device-looking modes into regular file or directory modes.

Fan-out functions include `XrdFfsPosix_unlinkall()`, `rmdirall()`, `renameall()`, `truncateall()`, `readdirall()`, `statvfsall()`, and `statall()`. Helper worker functions perform one per-server operation and are optionally scheduled through `XrdFfsQueue`.

`XrdFfsPosix_clear_from_rdr_cache()` creates then removes a path to force redirector cache updates after failed creates or renames.

## Control Flow

Mutating fan-out functions fetch data-server URLs from `XrdFfsMisc_get_all_urls()`, append the path, edit URLs for SSS identity, perform each operation in parallel when queues are enabled, then aggregate return codes and errno. Directory listing fan-out gathers `dirent` names from each server, merges/sorts via XrdFfsDent, filters duplicates plus `.lock`/`.fail` companions, caches the result, and returns an array.

`statall()` first tries a redirector stat when the task queue is deep or the directory cache suggests the file exists. Otherwise it stats each data server and returns the first successful result, with timeout handling for down hosts. `statvfsall()` queries XRootD xattrs for total/free/used space and aggregates block counters across servers.

## State and Persistence Behavior

The simple wrappers mutate remote XRootD namespace state. Fan-out functions can delete, rename, truncate, or query files on every cached data server. Local state is temporary arrays of URLs, job handles, per-server errno/result buffers, and directory-cache updates.

## Dependencies and Integration Points

The implementation depends on `XrdPosixXrootd`, XrdCl filesystem/URL APIs, `XrdFfsMisc`, `XrdFfsDent`, and `XrdFfsQueue`. It is consumed by `XrdFfsWcache` and `XrdFfsXrootdfs`.

## Risks and Edge Cases

Several fixed-size URL buffers use manual `strncat()` arithmetic; one `statall()` append uses `MAXROOTURLLEN - strlen(path) - 1` instead of remaining destination space. Fan-out mutations are not atomic across servers, so partial success can leave inconsistent namespace state. `statall()` initializes `max_mtime` inside the loop, so the intended latest-mtime selection does not actually compare across all results. Error aggregation favors early non-ENOENT failures and timeout behavior.

## Test Signals

Tests should cover wrapper errno propagation, xattr subclass parsing, fan-out success/partial failure/down-host handling, directory merge and cache behavior, `statall()` fast path, `.lock`/`.fail` filtering, and non-atomic mutation recovery scenarios.
