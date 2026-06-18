# sources/distributed-fs/xrootd/src/XrdFfs/XrdFfsXrootdfs.cc

## Purpose

This file implements the `xrootdfs` FUSE executable, presenting an XRootD storage cluster as a mounted filesystem. It wires FUSE callbacks to XrdFfs POSIX wrappers, data-server fan-out, write/read cache behavior, optional CNS shadow namespace updates, and optional SSS user identity handling.

## Important APIs, Types, and Functions

`struct XROOTDFS` stores command/environment options: redirector URL, CNS URL, fast stat mode, daemon uid, SSS keytab, URL cache lifetime, `ofs.fwd` behavior, worker count, and max virtual fd count. `xrootdfs_oper` maps FUSE operations to local static functions.

Important callbacks include `init`, `getattr`, `readdir`, `mknod`, `create`, `mkdir`, `unlink`, `rmdir`, `rename`, `truncate`, `open`, `read`, `write`, `statfs`, `release`, `fsync`, `setxattr`, and `getxattr`. `main()` parses FUSE and XrootdFS options, applies defaults, converts `xroot://` to `root://`, configures SSS env, installs SIGUSR1 handling, and calls `fuse_main()`.

## Control Flow

Initialization optionally drops privileges, creates `XrdPosixXrootd` with negative maxfd, initializes XrdFfs runtime, initializes Wcache with the virtual fd origin, derives `XRDEXPORTS`, starts worker threads, and restores the original working directory.

Per-operation control flow registers the calling FUSE uid/gid with SSS, constructs root URLs from redirector or CNS plus path, edits URLs for user identity, then calls XrdFfsPosix or Wcache functions. Metadata operations use CNS when configured and may use redirector/data-server fan-out depending on `ofsfwd`. File release flushes and destroys the cache, closes the data fd, and optionally updates CNS shadow file size/token metadata.

Operational controls are exposed through xattrs: refreshing/logging data servers and adjusting worker count. SIGUSR1 refreshes/logs the data-server cache in a detached thread.

## State and Persistence Behavior

Process state includes parsed mount options, worker pool, URL caches, directory/stat caches, SSS registrations, and Wcache descriptors. Persistent effects are remote XRootD file/namespace mutations, optional CNS shadow files, and syslog messages. FUSE cache timeouts differ for EC mode by setting entry timeout to zero.

## Dependencies and Integration Points

The executable depends on FUSE 2.6 API, XrdFfsPosix, XrdFfsMisc, XrdFfsWcache, XrdFfsQueue, XrdFfsFsinfo, and XrdPosixXrootd. It integrates with environment variables such as `XROOTDFS_RDRURL`, `XROOTDFS_CNSURL`, `XROOTDFS_FASTLS`, `XROOTDFS_USER`, `XROOTDFS_OFSFWD`, `XROOTDFS_NWORKERS`, `XROOTDFS_MAXFD`, `XROOTDFS_NO_ALLOW_OTHER`, and `XRDCL_EC`.

## Risks and Edge Cases

Many URL buffers are fixed 1024-byte arrays assembled by `strncat()`. `xrootdfs_init()` builds `exportpath` without initializing it before `strcat()`. `xrootdfs_readdir()` returns `-errno` after a successful fan-out listing, so stale errno can affect success. Several callbacks intentionally no-op permission/time/link operations, which may surprise POSIX applications. Shadow CNS updates are best-effort and can diverge from data files.

## Test Signals

Tests should cover mount option parsing, environment defaults, create/open/write/read/release flows, CNS and non-CNS metadata behavior, EC mode read bounds and FUSE timeouts, xattr controls, SIGUSR1 refresh, SSS URL rewriting, and error propagation through FUSE negative errno returns.
