# sources/distributed-fs/xrootd/src/XrdOss/XrdOssCopy.cc

## Purpose
Implements file-copy support used by relocation. It optimizes same-filesystem copies with hard links, otherwise copies data in mmap-backed segments with a traditional pread/pwrite fallback, then copies xattrs and preserves mtime.

## Important APIs, types, and functions
`XrdOssCopy::Copy(inFn, outFn, outFD)` owns the input fd and the pre-opened output fd through local RAII wrappers. It stats both files, hard-links when source and destination devices match, copies in 1 MiB segments via `mmap()` and `Write()`, falls back to buffered `pread()` only when no segment was copied, copies extended attributes through `XrdSysFAttr::Xat->Copy()`, and sets atime/mtime with `utime()`. `Write()` is a retry loop around `pwrite()` that handles EINTR and returns logged negative errors.

## Control flow
The fast path is: open input, stat input/output, resolve symlink source if needed, unlink output placeholder, create a hard link, return file size. The cross-device path maps each segment and writes it. If mmap fails before any data transfer, it logs and attempts a full traditional copy. Partial mmap failure after some bytes returns `-EIO`.

## State and persistence
No global state is modified. Persistence effects are the destination file content, copied extended attributes, and destination timestamps. The output fd is always closed by the local wrapper.

## Dependencies and integration points
Used by `XrdOssReloc.cc`. Depends on POSIX file APIs, `mmap`, `utime`, `XrdSysFAttr`, `OssEroute`, and `OssTrace`. It assumes the caller already created/preallocated the destination file descriptor and handles cleanup on failure.

## Risks and test signals
The fallback only runs if nothing was copied; failures after partial mmap writes leave cleanup to the caller. Hard-linking a symlink requires careful `lstat/readlink` behavior. Tests should cover same-device regular files and symlinks, cross-device copy, mmap failure fallback, EINTR handling, xattr copy failures, timestamp preservation, and cleanup behavior when `Copy()` returns a negative code.
