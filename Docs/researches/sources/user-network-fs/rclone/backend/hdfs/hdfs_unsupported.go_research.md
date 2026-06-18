
# sources/user-network-fs/rclone/backend/hdfs/hdfs_unsupported.go

## Purpose
This Plan 9-only stub keeps the `hdfs` package buildable on unsupported platforms by providing a package declaration when the real HDFS files are excluded.

## Important APIs, Types, And Control Flow
The file has only the `//go:build plan9` tag and `package hdfs`; it defines no registration, options, types, or functions.

## State And Persistence
There is no runtime state or persistence.

## Dependencies And Integration Points
Its only integration point is Go build selection. On Plan 9, importing this package succeeds as an empty package, but the backend is not registered.

## Risks And Test Signals
The main risk is accidental use expecting `NewFs` or `Object` on Plan 9; those symbols do not exist. Compile tests on Plan 9-like build tags are the relevant signal.
