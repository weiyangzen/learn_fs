## sources/distributed-fs/xrootd/src/XrdPosix/XrdPosixObject.cc

Purpose: implements the shared descriptor-table and object lookup/release machinery for XrdPosix file and directory objects.

Important APIs/functions: `AssignFD`, `Dir`, `File`, `Init`, `Release`, `ReleaseDir`, `ReleaseFile`, and `Shutdown`.

Control flow: `Init()` opens `/dev/null`, raises/reads `RLIMIT_NOFILE`, allocates `myFiles`, and optionally sets a virtual-FD base when `fdnum` is negative. `AssignFD()` either finds a virtual slot or duplicates `/dev/null` to obtain a real FD, then stores `this` in `myFiles` and sets `fdNum`. `File()`/`Dir()` validate descriptor range, fetch the object under global `fdMutex`, downcast through `Who()`, try to acquire object read/write lock with bounded retries, and return the typed object. Release paths remove table entries and close real shadow FDs when used. `Shutdown()` deletes all registered objects.

State and persistence: static in-memory descriptor table, high/last/base/free FD counters, and `/dev/null` FD. No durable state.

Dependencies/integration: uses `XrdSysMutex`, object locks from `XrdPosixObject.hh`, `XrdSysTimer`, POSIX resource limits, and thread-local `ecMsg`. All file/directory wrappers rely on this registry to distinguish XRootD descriptors from native descriptors.

Risks: descriptor shadowing assumes applications do not close shadow FDs behind XrdPosix; detection logs but continues. Lookup can wait up to roughly one minute, then returns `ETIMEDOUT`. `Init()` may raise process FD limits to `maxFD`. Release always unlocks `fdMutex`, so callers must pass `needlk` accurately. Shutdown deletes objects while bypassing delayed close logic.

Test signals: FD assignment in real and virtual modes; stream FD limit behavior; invalid descriptor returns `EBADF`; lookup timeout under held object lock; release/free slot reuse; shutdown cleanup.
