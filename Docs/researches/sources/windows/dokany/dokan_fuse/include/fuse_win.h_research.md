# File Research: sources/windows/dokany/dokan_fuse/include/fuse_win.h

Windows portability header for FUSE compatibility.

Key contents:
- Defaults `FUSE_USE_VERSION` to 27.
- Defines default volume and filesystem names.
- Declares errno/NTSTATUS translation helpers and MSVC wide-argument conversion helpers.
- Declares global wide strings for Dokan filesystem and volume names.
- Fills missing POSIX-ish types and structs for MinGW/MSVC:
  - `gid_t`, `uid_t`, `pid_t`, `nlink_t`, `blksize_t`, `blkcnt_t`, `uint64_t`;
  - `timespec` when absent;
  - `statvfs`;
  - `flock`.
- Forces wide offset mode with `FUSE_OFF_T __int64`.
- Defines `stat64_cygwin` as the adapter’s `FUSE_STAT`.
- Defines simple locking constants `F_WRLCK`, `F_UNLCK`, `F_SETLK`.

Role:
- Provides enough Unix type surface for FUSE code to compile on Windows toolchains.
