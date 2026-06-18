<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdFrc/XrdFrcXLock.hh -->
# sources/distributed-fs/xrootd/src/XrdFrc/XrdFrcXLock.hh

## Purpose
`XrdFrcXLock.hh` defines a minimal RAII serialization helper around `XrdOucSxeq`. It gives FRM code a shared process/file lock for critical sections rooted at an admin path.

## Important APIs
`XrdFrcXLock::Init(aPath)` creates an `XrdOucSxeq` named `.frmxeq` under the supplied path and detaches its file descriptor into the static `lkFD`. Constructing `XrdFrcXLock` calls `XrdOucSxeq::Serialize(lkFD, 0)`, and destruction calls `XrdOucSxeq::Release(lkFD)`.

## Control Flow And State
The only state is the static `lkFD`, initialized to `-1` in this header unless `__FRCXLOCK_CC__` is already defined. The class assumes `Init()` is called before any RAII object is constructed. Locking and unlocking are scoped to C++ object lifetime.

## Dependencies And Integration Points
The helper depends solely on `XrdOucSxeq`. It integrates with FRM code that needs cross-process serialization around queue/admin metadata updates. The header-local static definition avoids a separate `.cc` file but requires careful include discipline.

## Risks And Test Signals
The header defines storage for `lkFD` in every translation unit unless include guards and `__FRCXLOCK_CC__` behavior prevent duplication in the actual build model; that pattern can be fragile with modern linkers and shared libraries. Constructing before successful `Init()` serializes on `-1`. Tests should cover initialization failure, nested lock scopes, multi-process contention, and link builds with multiple consumers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/xrootd/src/XrdFrc/XrdFrcXLock.hh -->
