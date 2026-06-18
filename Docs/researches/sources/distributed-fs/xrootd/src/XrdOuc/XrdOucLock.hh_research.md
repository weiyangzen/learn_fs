<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOuc/XrdOucLock.hh -->
# sources/distributed-fs/xrootd/src/XrdOuc/XrdOucLock.hh

Purpose: Provides a tiny RAII lock guard for `XrdSysMutex`.

APIs and control flow: `XrdOucLock(XrdSysMutex*)` stores the mutex pointer, locks it immediately, and records `isLocked`. The destructor unlocks if still marked locked. There is no public unlock/relock API, so instances are intended for stack-scoped critical sections.

State and persistence: Holds only a borrowed mutex pointer and a local locked flag. No persistent state or ownership transfer exists.

Dependencies and integration: Depends on `XrdSys/XrdSysPthread.hh`. It integrates with older XRootD code that predates or avoids standard C++ lock guards.

Risks and test signals: The class assumes a non-null mutex and is copyable by default, which could double-unlock if copied. Tests should exercise scope-exit unlock behavior, exception/early-return paths, and avoid copying in callers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdOuc/XrdOucLock.hh -->
