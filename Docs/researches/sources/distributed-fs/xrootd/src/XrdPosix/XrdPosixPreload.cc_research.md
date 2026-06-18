<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdPosix/XrdPosixPreload.cc -->
# sources/distributed-fs/xrootd/src/XrdPosix/XrdPosixPreload.cc

Purpose: Exports the LD_PRELOAD/libc interposition layer for the 64-bit POSIX API. Each `extern "C"` function initializes `XrdPosixLinkage` once and forwards intercepted libc-style calls to the XRootD POSIX wrapper functions in `XrdPosixExtern.hh`, or to native libc via `Xunix` in lite mode.

Important APIs/types/functions: The file wraps `access`, `acl`, `chdir`, `close`, `closedir`, `creat64`, `fclose`, `fcntl64`, `fdatasync`, `fflush`, `fopen64`, `fread`, `fseek`, `fseeko64`, `fstat64` or `__fxstat64`, `fstatat64`, `fsync`, `ftell`, `ftello64`, `ftruncate64`, `fwrite`, Linux xattr calls, `lseek64`, `llseek`, `lstat64` or `__lxstat64`, `mkdir`, `open64`, `openat`, `opendir`, `pathconf`, `pread64`, `pwrite64`, `read`, `readv`, `readdir64`, `readdir64_r`, `rename`, directory positioning, `stat64` or `__xstat64`, `statfs64`, `statvfs64`, optional `statx`, `truncate64`, `unlink`, `write`, and `writev`.

Control flow and state: Each wrapper uses a function-local static `Init = Xunix.Init(&Init)` to avoid repeated initialization. `isLite` is initialized from `XRD_POSIX_PRELOAD_LITE`; when true, selected namespace/directory operations bypass the XRootD POSIX layer and call native libc through `Xunix`. The file also adapts Linux versioned stat entry points and platform conditionals.

Dependencies/integration: It is the user-facing preload entrypoint over `XrdPosix_*` C wrappers and `XrdPosixLinkage`. It depends on OS compatibility macros from `XrdPosixOsDep.hh` and musl cleanup of redirected symbol names.

Risks and test signals: Interposition bugs can deadlock during initialization, recurse into wrappers, or mishandle variadic `open/fcntl` arguments. Test signals include preload smoke tests for local and `root://` paths, lite mode behavior, xattr/stat/statfs wrappers, openat/fstatat handling, and musl/glibc versioned symbol builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdPosix/XrdPosixPreload.cc -->
