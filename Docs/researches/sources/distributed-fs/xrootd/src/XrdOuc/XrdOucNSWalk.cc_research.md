<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOuc/XrdOucNSWalk.cc -->
# sources/distributed-fs/xrootd/src/XrdOuc/XrdOucNSWalk.cc

Purpose: Implements directory indexing and optional recursive namespace traversal with stat/link collection, exclude lists, lock-file coordination, and empty-directory callbacks.

APIs and control flow: `Index()` processes queued directories one at a time, optionally locks a named file, calls `Build()`, and returns a linked list of `NSEnt` entries. `Build()` opens the directory, reads entries, skips `.`/`..`, gets stat data using `fstatat()` when available, queues child directories when recursive traversal is enabled, reads symlink targets when requested, applies return-type filters, and orders entries by option. `LockFile()` opens and write-locks the configured lock file. `setPath()` maintains a mutable path buffer with `File` pointing at the filename suffix.

State and persistence: Traversal state lives in `DList`, `DEnts`, `DPath`, lock descriptors, and copied exclude lists. No persistent state is written, but filesystem locks may block other processes.

Dependencies and integration: Uses POSIX `opendir`, `readdir`, `stat`, `lstat`, `readlink`, `fcntl` locks, `XrdOucTList`, and `XrdSysError`.

Risks and test signals: `DPath` is fixed at 1032 bytes and path construction uses `strcpy`, so long paths are risky. Tests should cover recursion, symlink handling, skipped errors, lock files, empty callbacks, excludes, entry ordering, and path length boundaries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOuc/XrdOucNSWalk.cc -->
