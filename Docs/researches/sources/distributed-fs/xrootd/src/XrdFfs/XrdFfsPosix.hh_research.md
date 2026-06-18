# sources/distributed-fs/xrootd/src/XrdFfs/XrdFfsPosix.hh

## Purpose

This header declares C ABI wrappers for the XRootD POSIX client and the XrdFfs multi-server operations. It is the interface used by the FUSE executable and write/read cache layer.

## Important APIs, Types, and Functions

The first group mirrors POSIX filesystem calls: stat, directory iteration, mkdir/rmdir, open/lseek/read/pread/write/pwrite/close/fsync, unlink/rename/truncate, and getxattr. The second group exposes redirector-cache clearing and fan-out operations over all data servers: unlinkall, rmdirall, renameall, truncateall, readdirall, statvfsall, and statall.

## Control Flow

FUSE callbacks call these wrappers instead of direct libc calls. For ordinary open file descriptors, calls pass through to `XrdPosixXrootd`. Namespace-wide operations use the `*all` variants when `ofs.fwd` behavior is not requested.

## State and Persistence Behavior

The header itself has no state. The implementation mutates remote XRootD namespace and consults global caches from XrdFfsMisc and XrdFfsDent.

## Dependencies and Integration Points

It includes POSIX/FUSE-related system headers and is included by `XrdFfsXrootdfs.cc`, `XrdFfsWcache.cc`, and other XrdFfs utilities.

## Risks and Edge Cases

The header lacks include guards and exposes raw C pointers for arrays such as `char ***direntarray`; callers must understand allocation ownership. Function signatures use platform types such as `off_t`, `uid_t`, and `struct statvfs`, making ABI compatibility dependent on `_FILE_OFFSET_BITS` and platform headers.

## Test Signals

Compile coverage should validate 64-bit offset mode and repeated inclusion. Runtime signals come from wrapper/fan-out tests in the implementation and FUSE mount operations.
