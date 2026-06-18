# sources/object-store/minio/cmd/local-locker_gen.go

## Purpose

`local-locker_gen.go` is `tinylib/msgp` generated serialization code for lock diagnostics/state types: `localLockMap`, `lockRequesterInfo`, and `lockStats`. It supports efficient MessagePack encoding for lock inspection and grid/admin transport paths that need these structures.

## Important APIs, Control Flow, And State

`localLockMap` is encoded as a map from resource string to an array of `lockRequesterInfo`. Decode/unmarshal initialize or clear the destination map before filling it. `lockRequesterInfo` encodes nine exported fields: `Name`, `Writer`, `UID`, `Timestamp`, `TimeLastRefresh`, `Source`, `Group`, `Owner`, and `Quorum`; the internal `idx` is excluded by its `msg:"-"` tag. `lockStats` encodes `Total`, `Writes`, `Reads`, `LockQueue`, `LocksAbandoned`, and nullable `LastCleanup` as MessagePack time. All generated decoders skip unknown fields, and all methods wrap errors with field path context.

The generated methods define a binary schema but do not maintain lock state themselves. Dependencies are `time` and `github.com/tinylib/msgp/msgp`.

## Risks And Test Signals

Because `idx` is not serialized, decoded `lockRequesterInfo` is suitable for reporting but not for reconstructing a fully functional `localLocker` UID index without additional rebuild logic. Map iteration means serialized `localLockMap` order is nondeterministic. `local-locker_gen_test.go` validates zero-value round trips and benchmarks generated methods; it does not test populated lock maps, nullable/non-null `LastCleanup`, or unknown-field compatibility.
