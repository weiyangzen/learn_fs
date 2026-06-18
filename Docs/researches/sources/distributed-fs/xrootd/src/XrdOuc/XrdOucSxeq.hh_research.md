# sources/distributed-fs/xrootd/src/XrdOuc/XrdOucSxeq.hh

Purpose: declares `XrdOucSxeq`, a serialization lock wrapper around lock files and file descriptors.

Important APIs, types, and functions: option constants are `noWait`, `Share`, `Unlink`, and `Lock`. Public methods include `Detach()`, object and static `Release()`, object and static `Serialize()`, `lastError()`, and two constructors for direct paths or suffix/dir composition.

Control flow: callers construct a lock object, optionally with immediate locking, use `Serialize()`/`Release()` to bracket critical work, and let the destructor close/unlink according to state. `Detach()` transfers descriptor ownership out of the object.

State and persistence: private members record filename, descriptor, unlink request, and last result. The file system lock file is the persistent coordination point.

Dependencies and integration points: the header has no includes beyond its guard, keeping the declaration lightweight for utilities needing cross-process serialization.

Risks and test signals: copy operations are not disabled despite owning a descriptor and filename. Tests should ensure objects are not copied accidentally, and should verify `Detach()` prevents destructor close of externalized descriptors.
