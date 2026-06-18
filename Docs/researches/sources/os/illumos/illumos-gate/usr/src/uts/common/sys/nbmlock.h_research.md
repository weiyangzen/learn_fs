# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/nbmlock.h

Non-blocking mandatory-locking support interface.

Key responsibilities:
- Defines operation classes for mandatory lock/share conflict checks: read, write, rename, remove, and read-write mmap/exclusive checks.
- Declares critical-region primitives for vnode mandatory-lock-sensitive operations.
- Declares helpers to test whether checking is needed and to check generic, share, lock, and Solaris mandatory-lock conflicts.
- Declares `nbl_svmand()` for vnode/credential-based mandatory-lock setup or query.

Dependencies:
- Includes vnode, rwlock, and credential headers.

Notable risks:
- Correct caller use is operation-specific: `NBL_READWRITE` is for exclusive-lock or read-write mmap conflict checks, not ordinary I/O.
- These helpers protect filesystem operations from mandatory locking races; missing critical sections can violate locking semantics.
