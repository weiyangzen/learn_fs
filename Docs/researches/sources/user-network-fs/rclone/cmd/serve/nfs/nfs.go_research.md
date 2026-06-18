# sources/user-network-fs/rclone/cmd/serve/nfs/nfs.go

## Purpose

`nfs.go` registers `rclone serve nfs`, its RC entrypoint, options, cache enum, help text, and command runner for Unix builds.

## Important APIs, Types, and Functions

`OptionsInfo`, `handleCache`, `handleCacheChoices`, `Options`, global `Opt`, `AddFlags`, `Run`, and Cobra `Command` define the public command surface. Cache choices are memory, disk, and symlink.

## Control Flow

Initialization registers global options, adds VFS/NFS flags, registers the command, and installs RC serving. `Run` builds an Fs and VFS, creates an NFS server, and serves. Help text documents default localhost random-port behavior, no authentication, write-cache requirements, cache types, subpath mounts, and metadata handles.

## State and Persistence Behavior

Command state is in global options. Runtime server/cache state is handled by `server.go`, `handler.go`, and `cache.go`; disk/symlink cache options can persist handle mappings.

## Dependencies and Integration Points

It integrates Cobra, RC, rclone VFS, configstruct option parsing, and the Unix-only NFS server implementation.

## Risks and Test Signals

The command intentionally has no authentication and must default to localhost. Documentation says metadata suffix applies to `disk` and `cache`, likely intending `disk` and `symlink`. RC creation is tested in `nfs_test.go`; mount behavior is tested in handler/cache tests.
