<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdPosix/XrdPosixXrootd.hh -->
# sources/distributed-fs/xrootd/src/XrdPosix/XrdPosixXrootd.hh

Purpose: Declares the public static POSIX facade used by preload wrappers, direct clients, and PSS. The class documents the POSIX-like methods and XRootD-specific extensions and owns one-time descriptor-origin initialization through its constructor.

Important APIs/types/functions: The API includes POSIX calls (`Access`, `Close`, `Fstat`, `Fsync`, `Ftruncate`, `Lseek`, `Mkdir`, `Open`, `Opendir`, `Pread`, `Pwrite`, `Read`, `Readv`, `Readdir*`, `Rename`, `Rmdir`, `Stat`, `Statfs`, `Statvfs`, `Truncate`, `Unlink`, `Write`, `Writev`) plus extensions (`endPoint`, async read/write/fsync, `VRead`, `QueryChksum`, `QueryOpaque`, `QueryError`, `Getxattr`, `Fcntl`, `StatRet`, `isXrootdDir`, `myFD`). `isStream` is an internal open flag. `Fcop` currently exposes `QFInfo`.

Control flow and state: Static `baseFD` identifies the descriptor range owned by XRootD POSIX, and `initDone` guards one-time initialization. The constructor’s `maxfd` argument configures descriptor capacity; negative values request absolute max and no shadow descriptors per comments.

Dependencies/integration: Includes POSIX platform headers and `XrdPosixOsDep.hh`. It is the stable contract for `XrdPosixPreload*.cc`, `XrdPosixExtern` wrappers, and XrdPss files.

Risks and test signals: Because this header is a broad ABI/API contract, signature changes affect preload symbols and PSS. Tests should compile direct API users, preload builds, and PSS, and should validate documented extension semantics such as async `Open()` returning `-1`/`EINPROGRESS` while completing with the descriptor.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdPosix/XrdPosixXrootd.hh -->
