# sources/distributed-fs/xrootd/src/XrdOuc/XrdOucGMap.hh

## Purpose
Declares the grid-map interface used to translate security distinguished names into local user names.

## Important APIs, Types, And Functions
`XrdSecGMapEntry_t` stores a match value, mapped user, and match type. `XrdOucGMap` exposes `dn2user`, constructor macro `XrdOucGMapArgs`, `isValid`, and private `load`. Internal members include mapping hash, map filename/mtime, timeout, logger/tracer, debug flag, and `XrdSysXSLock`. The header also declares factory `extern "C" XrdOucgetGMap(XrdOucGMapArgs)`.

## Control Flow
Callers normally obtain an instance from the factory, check non-null validity implicitly, and call `dn2user` for connection setup. Reloading and lookup details are implemented in the `.cc`.

## State And Persistence
The class owns its mapping hash and runtime reload metadata. The mapfile is external persistent input.

## Dependencies And Integration Points
Includes `XrdOucHash`, `XrdOucString`, and `XrdSysXSLock`. The factory ABI and version-info recommendation are important for plugin loading.

## Risks And Test Signals
Risks include ABI drift in `XrdOucGMapArgs`, empty destructor despite owning a tracer pointer in the implementation, and performance sensitivity because mapping is used during physical connection creation. Test signals include factory loading, repeated mapping throughput, shared/exclusive lock behavior during reload, and version-info plugin checks.
