## sources/distributed-fs/xrootd/src/XrdPosix/XrdPosixObjGuard.hh

Purpose: provides an RAII guard for an `XrdPosixFile` that combines file reference management with the file update mutex.

Important APIs/types: `XrdPosixObjGuard` with constructor, destructor, `Init(XrdPosixFile*)`, and `Release()`.

Control flow: `Init()` releases any currently guarded file, stores the new file, increments its reference count, and locks its update mutex. `Release()` unreferences and unlocks, then clears the pointer. Destructor calls `Release()`.

State and persistence: holds one transient `XrdPosixFile *guardP`. No durable state.

Dependencies/integration: includes `XrdPosixFile.hh`; used where offset/size updates need lifetime and mutex protection together.

Risks: release order is `unRef()` before `updUnLock()`. If unref can delete the object immediately, unlocking afterward would be unsafe; correctness depends on reference/destruction semantics elsewhere. `Init()` does not handle null input. Copying is not disabled, so accidental copies could double-release.

Test signals: guard construction/destruction around mocked file refs/locks; reinitialization to another file; static analysis for copy usage; close/destruction races.
