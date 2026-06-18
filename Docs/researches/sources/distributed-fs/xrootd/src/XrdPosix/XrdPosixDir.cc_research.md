## sources/distributed-fs/xrootd/src/XrdPosix/XrdPosixDir.cc

Purpose: implements remote directory listing as POSIX `DIR`/`dirent64` style iteration over `XrdCl::DirectoryList`.

Important APIs/functions: `nextEntry(dirent64*)`, `StatRet(struct stat*)`, and `Open()`.

Control flow: `Open()` allocates a padded local `dirent64`, calls `DAdmin.Xrd.DirList()` with global directory-list flags, stores the returned directory vector, and returns a fake `DIR*` pointing at the object FD. `nextEntry()` lazily opens when needed, bounds iteration by `numEnt`, copies entry name and platform-specific inode/offset fields, optionally maps entry stat info into `myBuf`, then advances `nxtEnt`. `rewind()` in the header clears cached listing so the next call refetches.

State and persistence: per-object state includes `myDirVec`, allocated `myDirEnt`, optional stat output pointer, current/total entry counters, and last error. No durable state.

Dependencies/integration: uses `XrdPosixAdmin`, `XrdPosixMap::Result`, `XrdPosixMap::Entry2Buf`, and global `dlFlag` configured by `XrdPosixConfig`.

Risks: returned `DIR*` is not a real libc directory stream; only XrdPosix wrappers should consume it. Entry names are truncated to 256 bytes. `StatRet()` stores a caller-provided pointer and depends on the next `nextEntry()` call. Missing stat info becomes an error when stat output is requested.

Test signals: empty directory; long names; rewind and seek/tell behavior; directory listing with `DirlistAll` stat flags; `readdir_r` result/status propagation.
