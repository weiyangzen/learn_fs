# sources/distributed-fs/xrootd/src/XrdCms/XrdCmsPList.hh

Purpose: declares the path-list data structures that associate exported path prefixes with server availability masks. It is the public interface for path ownership lookup and mutation.

Important APIs/types: `XrdCmsPInfo` carries `rovec`, `rwvec`, and `ssvec` masks and exposes inline `And()`, `Or()`, and `Set()` helpers. `XrdCmsPList` stores one path entry and exposes `Next()`, `Path()`, and `PType()`. `XrdCmsPList_Anchor` owns the mutex and head pointer and provides `Add()`, `Empty()`, `Find()`, `First()`, `Insert()`, `NotEmpty()`, `Remove()`, `Type()`, and `Zorch()`.

Control flow: callers interact mostly with the anchor, which serializes mutation and lookup. `Empty()` and `Zorch()` support whole-list replacement or transfer, while `First()` is a raw head accessor.

State and persistence: path entries own `strdup()`-allocated pathnames and free them in their destructor. `pathtype` and `reserved` are present but unused in this subset. The structure persists only for the process lifetime.

Dependencies/integration: includes C string allocation helpers, `XrdCmsTypes.hh` for masks, and `XrdSysPthread.hh` for locking. It is a low-level dependency of CMS cache path tracking.

Risks: constructors do not handle `strdup()` failure. `XrdCmsPInfo::And()` mutates masks and returns whether anything remains, which can be misread as a pure predicate. `First()` and returned node pointers can race if used without anchor locking.

Test signals: compile tests should catch mask type width changes; unit-level tests should verify copy assignment, destructor cleanup under sanitizers, and anchor whole-list operations.
