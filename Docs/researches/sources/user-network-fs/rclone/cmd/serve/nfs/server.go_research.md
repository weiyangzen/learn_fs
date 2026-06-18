# sources/user-network-fs/rclone/cmd/serve/nfs/server.go

## Purpose

`server.go` owns the listening NFS server wrapper around go-nfs.

## Important APIs, Types, and Functions

`Server` stores options, handler, context, listener, and an `UnmountedExternally` flag. `NewServer`, `Addr`, `Shutdown`, and `Serve` are the public methods.

## Control Flow

`NewServer` warns when VFS cache mode is off, defaults an empty listen address to `localhost:`, creates a handler, binds a TCP listener, and returns the server. `Serve` logs the address and calls `nfs.Serve`; `Shutdown` closes the listener.

## State and Persistence Behavior

Server state is in memory. No persistent state is written here; handle cache persistence belongs to cache backends.

## Dependencies and Integration Points

It integrates rclone VFS, VFS cache mode, `NewHandler`, TCP networking, and the go-nfs serving loop.

## Risks and Test Signals

Risks include no authentication, listener-close shutdown semantics, writes being read-only without VFS cache, and go-nfs Serve error propagation. RC and handler tests cover construction paths but not a full client mount in this package.
