# sources/storage-engines/sqlite/tool/getlock.c

## Purpose
`getlock.c` inspects POSIX advisory locks on an SQLite database and, for WAL databases, the associated `-shm` file. It reports lock type and owning process ID when a conflicting lock is found.

## Important APIs, Types, and Functions
`usage()` prints the command form. `isLocked()` builds a `struct flock`, calls `fcntl(F_GETLK)`, and reports a lock if the kernel returns a conflicting lock. Constants encode SQLite rollback-lock bytes (`PENDING_BYTE`, `RESERVED_BYTE`, `SHARED_FIRST`, `SHARED_SIZE`) and WAL shared-memory lock offsets (`SHM_WRITE`, `SHM_CHECKPOINT`, `SHM_RECOVER`, read locks).

## Control Flow
`main()` opens the database read-only, reads and validates the 100-byte SQLite header, first checks for an exclusive lock over the shared-lock range, then branches on header byte 18 to distinguish rollback and WAL modes. Rollback mode checks pending, reserved, and shared locks on the database file. WAL mode opens `DATABASE-shm`, checks recovery, checkpoint, write, and read locks. If no locks are found, it prints `file is not locked`.

## State and Persistence
The tool is read-only. It opens file descriptors but does not modify database or shm files. It prints observations to stdout and errors to stderr.

## Dependencies and Integration Points
It is Unix-specific and depends on POSIX `open()`, `read()`, `fcntl()`, advisory locking semantics, and SQLite's default lock byte layout. It integrates with debugging and test workflows around database locking.

## Risks
It only works with Unix POSIX advisory locking and the usual `PENDING_BYTE`. WAL detection from the database header may be stale if mode changes are in flight. Missing `-shm` files are treated as errors for WAL-mode headers. Some early returns do not close descriptors or free `zShm`, which is acceptable for process exit but not library-style reuse.

## Test Signals
Run against unlocked rollback and WAL databases, databases with active readers/writers/checkpointers, invalid files, missing `-shm` files, and non-POSIX VFS scenarios. Reported lock names and PIDs should match known holding processes.
