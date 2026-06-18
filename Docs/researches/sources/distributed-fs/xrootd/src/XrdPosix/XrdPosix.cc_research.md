## sources/distributed-fs/xrootd/src/XrdPosix/XrdPosix.cc

Purpose: implements the exported C POSIX wrapper entry points that decide whether each operation targets XRootD or native Unix. It owns the global `XrdPosixXrootd Xroot`, `XrdPosixXrootPath XrootPath`, and references the native linkage vector `Xunix`.

Important APIs/functions: `XrdPosix_Access`, `Open`, `Openat`, `Fopen`, `Read`, `Write`, `Pread`, `Pwrite`, `Readv`, `Writev`, `Stat`, `Fstat`, `Fstatat`, `Statx`, `Opendir`, readdir variants, `Rename`, `Unlink`, `Truncate`, xattr wrappers, `XrdPosix_isMyPath`, and `XrdPosix_URL`. `XrdResolveLink()` is a local helper that follows local symlinks with `realpath()`/`readlink()` before URL classification. `fseterr()` and `fseteof()` manipulate libc `FILE` internals so stdio wrappers can report XRootD read/write status.

Control flow: path-based calls resolve links, pass the resolved path through `XrootPath.URL()`, then dispatch to `Xroot` for remote paths or `Xunix`/direct syscalls for local paths. Descriptor-based calls use `Xroot.myFD()` and directory calls use `Xroot.isXrootdDir()`. `Fopen()` translates mode strings to open flags, opens through `Xroot`, and wraps the returned descriptor with `fdopen()`. `Creat()` delegates to `Open()`.

State and persistence: no durable state is written here. Runtime state is in global XRootD path/FD registries and libc streams. `Chdir()` updates `XrootPath.CWD()` only after native `chdir()` succeeds.

Dependencies/integration: integrates with `XrdPosixXrootd`, `XrdPosixXrootdPath`, `XrdPosixLinkage`, `XrdSysStatxHelpers`, libc, and platform syscalls. It is the LD-preload or macro-facing boundary for applications.

Risks: symlink resolution uses fixed 2048/2049 buffers and only follows 10 links. Some local fallback paths call raw syscalls instead of `Xunix`, creating platform-specific behavior. `Fcntl()` returns success for XRootD FDs without implementing command semantics. `Statx()` calls `XrdPosix_Stat()` with an already translated path, which is worth regression testing. FILE flag manipulation is libc-layout-sensitive.

Test signals: exercise local-vs-remote dispatch for all wrappers; remote stdio EOF/error behavior; symlink to remote URL; `openat`/`fstatat` with and without `AT_SYMLINK_NOFOLLOW`; xattr unsupported cases; directory iteration; `statx` conversion; mixed local and XRootD descriptors.
