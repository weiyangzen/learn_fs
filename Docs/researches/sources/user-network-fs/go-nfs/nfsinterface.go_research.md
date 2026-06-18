# sources/user-network-fs/go-nfs/nfsinterface.go

## Purpose

`nfsinterface.go` defines the NFSv3 procedure and status enumerations used by the server and exposes small common wire structures. It is the shared type surface that lets handlers identify procedure numbers, convert them to readable names, emit NFS status codes, and decode common directory operation arguments.

## Important APIs, Types, and Functions

`NFSProcedure` is a `uint32` enum for procedures from `NULL` through `COMMIT`, with `String()` returning human-readable names. `NFSStatus` is a `uint32` enum for NFSv3 status values such as `NFSStatusOk`, `NoEnt`, `Access`, `Stale`, `NotSupp`, and `ServerFault`, with `String()` mapping codes to messages. `DirOpArg` carries a parent handle and filename for operations such as lookup, create, remove, mkdir, and symlink.

## Control Flow

There is no dynamic control flow beyond switch-based string conversion. Server dispatch code uses procedure numeric values to select registered handlers, handlers return `NFSStatusError` values containing these status constants, and XDR response writers serialize these constants as `uint32`.

## State and Persistence Behavior

The file is stateless. Constants are compile-time values and `DirOpArg` instances are request-local decoded structures. There is no filesystem, network, or process-global mutation.

## Dependencies and Integration Points

The constants correspond to NFSv3 procedure and `nfsstat3` values and are used across handler registration, request logging, response construction, and client-visible error mapping. `DirOpArg` is consumed by handlers such as `onSymlink`.

## Risks and Edge Cases

Incorrect numeric constants would break wire compatibility. The `NFSStatusOk` string contains a typo (`Successfull`), which affects logs or diagnostics but not protocol behavior. Unknown procedures and statuses stringify to generic values, which is safe but can hide missing enum additions. `DirOpArg.Filename` is raw bytes, so each handler must enforce path/name policy consistently.

## Test Signals

Tests should verify procedure numbers against NFSv3 definitions, status constants against client expectations, and string values for logging. Integration tests that issue raw procedure IDs, such as `readDir` and `nfsRead` in `nfs_test.go`, indirectly verify selected procedure constants.
