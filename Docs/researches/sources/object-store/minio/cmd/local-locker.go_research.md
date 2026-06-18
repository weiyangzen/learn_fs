# sources/object-store/minio/cmd/local-locker.go

## Purpose

`local-locker.go` implements the local node side of MinIO's distributed lock interface (`dsync.NetLocker`). It maintains in-memory read/write locks for object resources, tracks lock UIDs for refresh and force-unlock, rejects overload, and expires stale locks.

## Important APIs, Types, Control Flow, And State

`lockRequesterInfo` records resource name, writer/read mode, UID, timestamps, source, group flag, owner, quorum, and an internal resource index. `localLocker` protects `lockMap` (`resource -> []lockRequesterInfo`) and `lockUID` (`UID+index -> resource`) with a mutex and tracks waiters, read/write stats, cleanup time, and overload count with atomics. `Lock` rejects too many resources, overload, canceled contexts, and any already-locked resource; otherwise it writes one lock entry per resource and one UID index per resource. `RLock` only accepts one resource and appends a reader if no writer exists. `Unlock` and `RUnlock` enforce write/read mode expectations and call `removeEntry`, which removes an entry only when UID and optional owner match.

`ForceUnlock` removes all locks for supplied resources when no UID is provided, or walks UID indexes to remove every resource held by a UID. `Refresh` updates `TimeLastRefresh` across all resources for a UID. `expireOldLocks` removes entries whose refresh timestamp exceeds the interval, updates read/write counters, and stores `lastCleanup`. `DupLockMap` returns a shallow copy for diagnostics; `IsOnline` and `IsLocal` report local availability.

All state is process-local memory. Persistence and cross-node behavior come from the surrounding grid/dsync layer, not this file.

## Risks And Test Signals

Risks include lockUID/lockMap divergence, duplicate read locks with the same UID, fairness/starvation under high contention, overloaded wait rejection causing retry storms, group-lock partial cleanup, and expiration under clock jumps. `local-locker_test.go` stresses large read/write sets, unlock/force-unlock cleanup, stale expiration, and UID accounting, including heavy cases skipped in short mode.
