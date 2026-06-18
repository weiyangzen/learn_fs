## sources/distributed-fs/xrootd/src/XrdSys/XrdSysDir.cc

Purpose: implements `XrdSysDir`, a small cross-platform directory iteration wrapper.

Important APIs/types/functions: constructor opens a directory handle; destructor closes it; `nextEntry()` returns the next entry name or null; `isValid()` and `lastError()` are declared in the header. Unix uses `opendir`, `readdir`, and `closedir`. Windows uses `FindFirstFile`, `FindNextFile`, and `FindClose`.

Control flow: construction validates the path, opens the handle, and stores `errno`/`EINVAL`/`ENOTDIR` on failure. `nextEntry()` clears `lasterr`, validates the handle, calls platform iteration, and records only real errors.

State and persistence: per-object `void *dhandle` and `int lasterr`; no persistent storage. Returned `char *` points into platform-owned directory-entry storage and must be copied by callers that need it later.

Dependencies and integration: depends on `XrdSysDir.hh`, POSIX `dirent.h`, Windows APIs, `cerrno`, and `cstring`. Used wherever XrdSys needs portable directory traversal without exposing platform conditionals.

Risks: Windows constructor calls `FindFirstFile(path)` without appending a wildcard, so behavior depends on passed path shape. Returned pointer lifetime is short. `errno` is checked for `EBADF` only on Unix end-of-directory.

Test signals: valid/invalid paths, empty directories, permission-denied directories, end-of-directory without error, repeated `nextEntry()` calls, and Windows wildcard/non-wildcard paths.
