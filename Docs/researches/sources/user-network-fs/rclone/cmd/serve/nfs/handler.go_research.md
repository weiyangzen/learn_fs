# sources/user-network-fs/rclone/cmd/serve/nfs/handler.go

## Purpose

`handler.go` builds the go-nfs handler around rclone VFS, mount-path validation, handle-cache delegation, filesystem stats, and log bridging.

## Important APIs, Types, and Functions

`Handler` stores VFS, options, root `FS`, and `Cache`. `NewHandler`, `Mount`, `Change`, `FSStat`, `ToHandle`, `FromHandle`, `HandleLimit`, `InvalidateHandle`, and `Options.Limit` are core APIs. Logger methods implement go-nfs logging with rclone log levels. `OnUnmountFunc` and `onUnmount` provide external unmount signaling.

## Control Flow

`NewHandler` initializes cache and maps rclone log level to go-nfs level. `Mount` cleans requested dirpath under `/`, returns root FS for `/`, otherwise stats the target and only accepts plain directories, returning a sub-rooted FS. Handle methods delegate to cache with tracing. Logger `Tracef` detects `mount.Umnt` text to call unmount hooks.

## State and Persistence Behavior

Handler state is in memory; cache backend may persist separately. Subpath mounts share one root VFS and cache so handles stay stable.

## Dependencies and Integration Points

It integrates go-nfs mount/handler interfaces, go-billy, VFS statfs, rclone config logging, and cache implementations.

## Risks and Test Signals

Risks include text-based unmount detection, unauthenticated mount access, subpath mounts not isolating siblings/parents, and returning root FS even on mount rejection because go-nfs still needs a non-nil FS. Handler tests cover root/subpath/rejection/write/handle stability.
