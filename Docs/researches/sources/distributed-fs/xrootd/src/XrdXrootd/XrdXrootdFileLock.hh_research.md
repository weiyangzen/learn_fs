# sources/distributed-fs/xrootd/src/XrdXrootd/XrdXrootdFileLock.hh

Purpose: defines the abstract file lock manager interface used by xrootd file open/close handling. It separates protocol code from the concrete lock-table implementation.

Important APIs and types: `Lock(path, mode, force)` attempts to acquire a read or write lock and returns zero on success or a conflict count/sign on failure. `numLocks(path, rcnt, wcnt)` reports current reader and writer counts. `Unlock(path, mode)` releases a lock and returns status.

Control flow and state: this header has no state. Concrete implementations decide lock persistence and conflict policy.

Dependencies and integration: used by `XrdXrootdFile::Init()` and file destruction to enforce export/open locking. The default configured implementation in this subset is `XrdXrootdFileLock1`.

Risks and test signals: protocol code assumes unlock is available at file destruction and that lock modes match open modes. Tests should cover read/write conflict semantics in implementations and forced-lock behavior.
