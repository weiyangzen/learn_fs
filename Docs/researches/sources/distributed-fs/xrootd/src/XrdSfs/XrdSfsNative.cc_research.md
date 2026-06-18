# sources/distributed-fs/xrootd/src/XrdSfs/XrdSfsNative.cc

## Purpose
Implements the native POSIX-backed SFS filesystem used as the basic local filesystem adapter. It maps SFS directory, file, and namespace operations onto Unix system calls and exposes an `XrdSfsGetFileSystem()` factory.

## Important APIs, Types, And Functions
- `XrdSfsUFS` wraps POSIX `chmod`, `close`, `mkdir`, `open`, `unlink`, `rmdir`, `rename`, `fstat`, `stat`, and `truncate`.
- `XrdSfsNativeDirectory` implements `open()`, `nextEntry()`, and `close()`.
- `XrdSfsNativeFile` implements `open()`, `close()`, `fctl(SFS_FCTL_GETFD)`, scalar/vector reads and writes, synchronous AIO callbacks, `stat()`, `sync()`, and `truncate()`.
- `XrdSfsNative` implements filesystem-level `chmod`, `exists`, `fsctl`, `mkdir`, `Mkpath`, `rem`, `remdir`, `rename`, `stat`, `truncate`, and `Emsg`.
- `XrdSfsGetFileSystem()` returns a static `XrdSfsNative` instance.

## Control Flow
Directory open rejects reuse, stores the directory name, and calls `opendir()`. `nextEntry()` checks open state, preserves EOF once reached, and uses `readdir()` on Linux/GNU/FreeBSD-glibc or `readdir_r()` elsewhere. Close releases the directory handle and path string.

File open rejects reuse, translates SFS access/create/truncate flags to POSIX open flags, optionally creates parent directories with `Mkpath()`, opens the file, verifies it is a regular file, and maps directory/non-regular cases to errors. Reads and writes use `pread()`/`pwrite()` loops retrying `EINTR`. Vector reads require every element to transfer exactly the requested size. AIO methods execute synchronously, set `Result`, and call completion methods. Filesystem namespace methods call the corresponding POSIX operation and centralize error formatting through `Emsg()`.

## State And Persistence
The filesystem object is static and stores a static logger/error destination pointer. Directory instances hold `DIR *`, EOF state, and copied path. File instances hold a file descriptor and copied path. Persistence is entirely the underlying POSIX filesystem: creates, writes, truncates, renames, chmods, and removals affect local storage immediately, subject to `fsync()` when `sync()` is called.

## Dependencies And Integration Points
Depends on POSIX directory/file APIs, `XrdSysError`, `XrdSysE2T`, `XrdSysLogger`, `XrdSecInterface`, and SFS headers. Integrates as the native filesystem passed to higher-level filesystem plugins and as a fallback server filesystem implementation.

## Risks And Edge Cases
- `XrdSfsNativeFile::~XrdSfsNativeFile()` checks `if (oh) close();`; descriptor `0` would not be closed, while `-1` is truthy and calls `close()` harmlessly. Normally `open()` may return fd 0 in unusual environments, so this is worth auditing.
- `open()` stores `fname = strdup(path)` before all failure paths; failures before `close()` may leak `fname`.
- `mkdir()` calls `Mkpath()` for `SFS_O_MKPTH` but ignores its return before attempting the final `mkdir()`.
- `getMmap()` uses `if (Addr) Addr = 0`, which does not clear `*Addr`.
- `exists()` maps non-directory/non-regular existing objects to `XrdSfsFileExistNo` rather than `XrdSfsFileExistIsOther`.

## Test Signals
Run filesystem contract tests for create/open/truncate/read/write/sync/stat/rename/remove, directory iteration EOF and error reporting, path creation, large-offset guards on 32-bit builds, descriptor-return `fctl`, non-regular file open rejection, and failure cleanup after open errors.
