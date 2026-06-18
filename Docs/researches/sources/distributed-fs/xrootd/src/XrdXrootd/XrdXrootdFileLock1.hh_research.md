# sources/distributed-fs/xrootd/src/XrdXrootd/XrdXrootdFileLock1.hh

Purpose: declares the default in-memory implementation of the xrootd file lock interface for a single server per host.

Important APIs and types: `XrdXrootdFileLock1` implements `Lock()`, `numLocks()`, and `Unlock()` from `XrdXrootdFileLock`. It owns static `LTMutex` and a trace id in the implementation file. The destructor notes that the object is never destroyed in normal operation.

Control flow and state: lock table state is global to the implementation, not instance-local. This matches startup configuration that allocates one lock manager and installs it into `XrdXrootdFile`.

Dependencies and integration: includes pthread helpers and `XrdXrootdFileLock.hh`. It is created by `XrdXrootdProtocol::Configure()`.

Risks and test signals: inheritance is written without an explicit `public` keyword, so outside upcasts depend on construction/casts in implementation context; this is worth checking against compiler access expectations. Tests should compile and exercise the lock manager through the abstract interface and validate process-local semantics are documented for multi-server deployments.
