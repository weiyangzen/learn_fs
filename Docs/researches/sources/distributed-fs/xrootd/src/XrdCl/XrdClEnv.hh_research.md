# sources/distributed-fs/xrootd/src/XrdCl/XrdClEnv.hh

## Purpose
Declares `XrdCl::Env`, the client configuration store used by global defaults and command-specific execution contexts.

## Important APIs, Types, And Functions
Public APIs cover getting and putting strings, integers, and pointers; importing shell values; querying compiled defaults; and lock lifecycle methods `WriteLock`, `UnLock`, `ReInitializeLock`, and `RecreateLock`. Private `UnifyKey` lowercases keys and strips a leading `xrd_` prefix. The data members are an `XrdSysRWLock` and three maps.

## Control Flow
Callers use typed get/put/import APIs. The implementation normalizes all keys before accessing maps. The lock helpers support normal concurrent access and fork recovery: `ReInitializeLock` unlocks and reinitializes an existing lock, while `RecreateLock` placement-news a fresh lock in the same memory.

## State And Persistence
String and integer maps store both value and "imported from shell" status. Pointer map stores raw `void *` values. No ownership rules for pointers are expressed. State lives only in the `Env` instance and is not persisted to disk.

## Dependencies And Integration Points
Depends on standard containers/strings/algorithm and `XrdSysPthread.hh`. `DefaultEnv` derives from it; `FSExecutor` owns an `Env` for CLI state; many client modules consume default values through `DefaultEnv::GetEnv()`.

## Risks
Manual lock lifecycle methods are unusual and can be unsafe if used outside fork recovery. Key normalization uses `::tolower` directly on `char`, which is locale/negative-char sensitive. Pointer storage is type-erased and unowned. Because write locking is exposed, external code can hold the lock while calling back into env methods and risk deadlock.

## Test Signals
Header-level tests should cover key normalization, lock recreation after fork-like scenarios, type-specific map separation, and compilation under consumers that subclass or embed `Env`. ABI checks matter because `Env` is part of the installed public header set.
