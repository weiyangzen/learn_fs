# sources/distributed-fs/xrootd/src/XrdSys/XrdSysPriv.cc

Purpose: implements process privilege switching for Unix-like builds, including temporary effective UID/GID changes through `XrdSysPrivGuard` and permanent privilege drops through `XrdSysPriv::ChangePerm()`.

Important APIs/types/functions: `XrdSysPriv::Restore()`, `ChangeTo()`, `ChangePerm()`, `DumpUGID()`, `XrdSysPrivGuard` constructors/destructor, and `XrdSysPrivGuard::Init()` are the behavioral surface. Local fallback implementations of `setresuid`, `setresgid`, `getresuid`, and `getresgid` cover platforms without native `setres*` APIs. `XSPERR(errno)` maps failures to negative errno-style returns.

Control flow: `ChangeTo()` records the current effective IDs, restores real privileges if needed, then sets effective GID and UID while saving the old effective values. `Restore(saved)` restores either saved or real IDs as effective IDs. `ChangePerm()` locks the global recursive mutex, restores real privileges, sets all real/effective/saved IDs to the new values, verifies the result, and unlocks. `XrdSysPrivGuard::Init()` locks the global mutex, checks current IDs, temporarily changes identity only when running with real UID 0, and leaves the lock held until the guard destructor restores saved privileges.

State and persistence: global state is the process credential set; changes affect all threads, so `fgMutex` serializes operations. `XrdSysPrivGuard` stores only `dum` and `valid` flags, with `dum == false` meaning the guard changed credentials and owns the global mutex until destruction.

Dependencies and integration: uses `XrdSysRecMutex` from `XrdSysPthread.hh`, POSIX UID/GID APIs, `XrdSysPwd` for name-to-UID/GID lookup, and platform compatibility blocks for SGI/AIX/Linux/Cygwin. Windows builds compile no-op success paths for most operations.

Risks: credential state is process-wide, so any unguarded thread doing filesystem or security-sensitive work while a guard is active observes the temporary identity. Several error paths return without unlocking in `DumpUGID()` when `getres*` fails after the mutex is locked. `ChangePerm()` is irreversible by design. Fallback `setres*` emulation cannot provide all saved-ID semantics of native APIs.

Test signals: run only in controlled privilege-aware tests. Validate name constructor with existing and missing users, non-root guard failure, root temporary switch and restoration, permanent drop behavior, and negative errno returns on invalid UIDs/GIDs.
