# sources/object-store/minio/cmd/erasure-common.go

Purpose: Provides utility methods on `erasureObjects` to select currently usable disks, especially local disks and non-healing online disks.

Important APIs/types/functions: `getOnlineDisks` randomizes disk order, concurrently calls `DiskInfo`, and excludes nil, inaccessible, and currently-healing disks. `getOnlineLocalDisks` filters the online set to local disks in randomized order. `getLocalDisks` returns local disks without probing `DiskInfo`.

Control flow and state: Disk probing uses goroutines, a mutex-protected result slice, and per-call random permutation seeded by current time. It does not persist state; it observes disk health through `StorageAPI.DiskInfo` and `IsLocal`.

Dependencies and integration points: Relies on `erasureObjects.getDisks`, `StorageAPI`, `DiskInfoOptions`, and `IsLocal`. Used by healing/listing code to avoid consuming unreachable or currently healing disks.

Risks: Random result ordering intentionally spreads load but can make behavior less deterministic. `getOnlineDisks` uses `context.Background`, so it does not honor caller cancellation. A disk transiently reporting `Healing` is skipped from selection.

Test signals: Coverage is indirect through healing/listing tests that rely on disk selection behavior.
