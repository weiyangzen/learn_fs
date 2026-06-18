<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdPosix/XrdPosixOsDep.hh -->
# sources/distributed-fs/xrootd/src/XrdPosix/XrdPosixOsDep.hh

Purpose: Provides standalone platform compatibility definitions for the POSIX preload/client layer. It normalizes 64-bit POSIX names and missing errno values across Solaris, macOS, FreeBSD, GNU/Hurd, and GNU/kFreeBSD without pulling in heavier XRootD platform headers.

Important APIs/types/functions: There are no functions. The header aliases `statfs64`, `dirent64`, `off64_t`, `stat64`, `statvfs64`, and `ELIBACC` where platform libc headers lack those symbols or use different names.

Control flow and state: Compile-time only. The file is included by preload and POSIX headers before symbol wrappers are defined, so macro ordering matters. It intentionally duplicates selected platform logic because it must be usable as a standalone include.

Dependencies/integration: Integrated with `XrdPosixPreload.cc`, `XrdPosixPreload32.cc`, and `XrdPosixXrootd.hh`. The wrappers depend on these aliases so exported `stat64`, `readdir64`, `statvfs64`, and offset APIs compile consistently.

Risks and test signals: Main risk is ABI drift with libc or OS headers. Incorrect aliases can cause wrapper signature mismatches, structure-size corruption, or missing symbols in preload builds. Build tests should cover Linux/glibc, macOS, FreeBSD, Solaris-like branches when available, and musl configurations that explicitly undefine libc redirections in the preload source.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdPosix/XrdPosixOsDep.hh -->
