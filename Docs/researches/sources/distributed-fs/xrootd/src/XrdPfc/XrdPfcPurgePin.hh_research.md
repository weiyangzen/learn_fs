# sources/distributed-fs/xrootd/src/XrdPfc/XrdPfcPurgePin.hh

## Purpose
Declares the purge plugin interface. `PurgePin` allows external policy code to request per-directory byte recovery based on a resource-monitor purge snapshot.

## Important APIs, Types, and Functions
- `DirInfo`: plugin result/config record with directory path, byte quota, bytes to recover, and an internal `DirUsage` pointer.
- `CallPeriodically()`: indicates whether the plugin wants to be invoked even without space/age pressure; default true.
- Pure virtual `GetBytesToRecover(const DataFsPurgeshot&)`: fills recovery needs and returns total bytes to remove.
- `ConfigPurgePin(const char*)`: optional configuration parser, default success.
- `refDirInfos()`: mutable access to directory recovery list consumed by purge driver.

## Control Flow
The cache loads or owns a `PurgePin`, configures it, and during purge checks calls `GetBytesToRecover`. The old purge driver then iterates `refDirInfos()` and purges each requested directory.

## State and Persistence Behavior
`PurgePin` stores in-memory policy/output list only. Persistent deletion is performed by the purge driver, not by the interface.

## Dependencies and Integration Points
Forward-depends on `DataFsPurgeshot` and `DirUsage`. Implementations must be ABI-compatible with the cache plugin loader; `XrdPfcPurgeQuota.cc` is one implementation.

## Risks and Test Signals
Risks include plugin-provided paths outside intended cache scope, stale `DirUsage*` pointers after a purge snapshot, and default periodic invocation causing unexpected purge scans. Tests should validate plugin configuration, snapshot lookup failures, and empty/zero recovery lists.
