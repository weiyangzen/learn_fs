# sources/user-network-fs/rclone/fs/types.go

## Purpose
This file defines core filesystem interfaces and shared support types for rclone. These interfaces form the contract every backend and many wrappers must implement.

## Important APIs, Flow, and State
`Fs` embeds `Info` and requires `List`, `NewObject`, `Put`, `Mkdir`, and `Rmdir`. `Info` exposes backend identity, root, precision, supported hashes, and optional `Features`. `Object` embeds `ObjectInfo` and requires mutation/read methods. `ObjectInfo`, `DirEntry`, and `Directory` define common object and directory metadata. Optional interfaces cover MIME type, IDs, unwrap, storage tier, metadata, and directory modtime setting. Aggregate interfaces `FullDirectory`, `FullObjectInfo`, and `FullObject` help wrappers assert broad support.

`ObjectOptionalInterfaces` and `DirectoryOptionalInterfaces` use type assertions to report supported/unsupported optional capabilities. `ListRCallback` and `ListRFn` define recursive listing callbacks. `Flagger` and `FlaggerNP` define config value contracts. `NewUsageValue` clamps numeric usage values to `math.MaxInt64`, and `Usage` models quota/about fields. `Unknown` is a placeholder `Info`.

## Dependencies, Integration, Risks, and Test Signals
The file imports `context`, `encoding/json`, `io`, `math`, `time`, and `fs/hash`. It is central to backends, operations, sync, walk, filter, metadata, accounting, and tests. Changing interface signatures or semantics has high blast radius. Optional-interface reporting can drift when new optional interfaces are introduced. Direct tests are distributed; this subset exercises these contracts through sync, walk, and `Tristate` flag tests.
