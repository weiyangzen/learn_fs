
# sources/user-network-fs/rclone/backend/hdfs/object.go

## Purpose
This file implements HDFS object behavior: metadata access, range-capable reads, whole-object replacement writes, modtime updates, removal, and rclone object interface conformance.

## Important APIs, Types, And Control Flow
`Object` stores parent `Fs`, remote path, size, and modtime. `Open` opens an HDFS file, applies `SeekOption` or `RangeOption`, seeks to the requested offset, and wraps the reader with `readers.NewLimitedReadCloser` when a limit is set. `Update` creates parent directories, removes any existing target, creates a new file, copies input, closes with pacer retry for `hdfs.ErrReplicating`, stats the final object, sets modtime via `Chtimes`, and updates cached size. `Hash` always returns `hash.ErrUnsupported`.

## State And Persistence
Persistent effects are HDFS writes, deletion of any replaced object, chmod-like timestamp changes through `Chtimes`, and removal via `client.Remove`. Object fields cache the latest size and modtime after successful stat and timestamp operations.

## Dependencies And Integration Points
It uses the HDFS client from `Fs`, rclone open options, `readers.NewLimitedReadCloser`, and the `Fs` pacer for close retry. It integrates with the `Put` method in `fs.go`, which constructs an `Object` and delegates to `Update`.

## Risks And Test Signals
`Update` removes an existing destination before creating the replacement, so a copy or close failure can leave no old object and a cleanup attempt for the partial new file. `Open` does not explicitly reject negative offsets before `Seek`; HDFS seek behavior handles errors. The `ErrReplicating` close path is important because HDFS can acknowledge data before NameNode lease closure. Tests should cover overwrite failure cleanup, range reads, modtime persistence, unsupported hashes, and close retry behavior.
