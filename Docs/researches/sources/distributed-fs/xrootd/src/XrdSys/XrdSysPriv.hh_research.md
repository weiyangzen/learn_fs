# sources/distributed-fs/xrootd/src/XrdSys/XrdSysPriv.hh

Purpose: declares the privilege-management API and intentionally restricts most operations to `XrdSysPrivGuard`, encouraging scoped temporary identity changes.

Important APIs/types/functions: `XrdSysPriv` exposes only `ChangePerm()` publicly; `ChangeTo()`, `Restore()`, and `DumpUGID()` are private static helpers available to the friend `XrdSysPrivGuard`. `XrdSysPrivGuard` provides constructors by numeric UID/GID or username, a destructor for restoration, and `Valid()` for status.

Control flow: callers create a guard in a scope, test `Valid()`, perform work under the temporary identity, and rely on the destructor to restore the previous saved credentials. Permanent drops use `XrdSysPriv::ChangePerm()` directly.

State and persistence: declares the static recursive mutex `fgMutex` and debug flag `fDebug`. Guards persist no credential snapshot themselves; the implementation relies on saved UID/GID slots and the global mutex.

Dependencies and integration: includes `sys/types.h` on non-Windows and defines placeholder `uid_t`/`gid_t` on Windows. It depends on `XrdSysPthread.hh` for `XrdSysRecMutex` and is used by code needing privileged open, chown, or user-context filesystem operations.

Risks: the guard API can serialize changes but cannot isolate credentials per thread. `Valid()` must be checked when a switch is required; otherwise code may continue under the original identity. The username constructor depends on passwd lookup availability.

Test signals: compile on Unix and Windows, exercise RAII restore on normal scope exit, and verify failures do not leave the global mutex locked.
