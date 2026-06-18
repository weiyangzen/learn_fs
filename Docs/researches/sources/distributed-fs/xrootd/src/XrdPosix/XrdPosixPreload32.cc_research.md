<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdPosix/XrdPosixPreload32.cc -->
# sources/distributed-fs/xrootd/src/XrdPosix/XrdPosixPreload32.cc

Purpose: Supplies 32-bit ABI-compatible preload wrappers and structure conversion helpers when building on environments where 32-bit POSIX entry points coexist with the 64-bit XRootD POSIX implementation. It is guarded by LP64-related conditionals and disables large-file macro remapping for the ABI surface it defines.

Important APIs/types/functions: `XrdPosix_CopyDirent()` converts `dirent64` into `dirent` with overflow detection. `XrdPosix_CopyStat()` converts `stat64` to `stat`, saturating selected fields or returning `EOVERFLOW` for regular files/directories too large for the ABI. Wrappers include `creat`, `fcntl`, `fseeko`, `fstat`/versioned variants, `fstatat`, `ftello`, `ftruncate`, `lseek`, `lstat`, `open`, `pread`, `pwrite`, `readdir`, `readdir_r`, `stat`, `statfs`, `statvfs`, and `truncate`.

Control flow and state: Like the 64-bit preload file, each wrapper initializes `Xunix` once. For path/stat wrappers on Linux and macOS, non-XRootD paths may be passed to native `Xunix` based on `XrdPosix_isMyPath()` or `XrdPosixXrootd::myFD()`. XRootD paths use the 64-bit internal calls and are converted down to ABI structures as needed.

Dependencies/integration: Works with `XrdPosixPreload.cc`, `XrdPosixExtern.hh`, `XrdPosixXrootd.hh`, and platform macros. `XRD_POSIX_PRELOAD_LITE` again influences directory reads.

Risks and test signals: Main risks are overflow handling, wrong structure layout assumptions, and accidental interception of non-XRootD paths. Tests should exercise large file sizes, large inode/offset fields, versioned stat symbols, 32-bit readdir conversion, FreeBSD/Solaris exclusions, and local passthrough for regular files.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdPosix/XrdPosixPreload32.cc -->
