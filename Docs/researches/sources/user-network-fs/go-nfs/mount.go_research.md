<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-nfs/mount.go -->
# sources/user-network-fs/go-nfs/mount.go

## Purpose
Registers and implements the ONC mount protocol procedures needed by NFS clients.

## Important APIs, Types, and Functions
`onMountNull`, `onMount`, and `onUMount` are registered for mount service procedures.

## Control Flow
`onMount` reads the requested dirpath, calls `Handler.Mount`, writes RPC success, encodes mount status, and when OK writes the root file handle and auth flavors. `onUMount` consumes the opaque path and acknowledges.

## State and Persistence Behavior
No server-side mount table is maintained; state is delegated to the handler and handle cache.

## Dependencies and Integration Points
Depends on `RegisterMessageHandler`, `MountRequest`, XDR, and `Handler.ToHandle`.

## Risks and Edge Cases
Auth is TODO; unmount does not invalidate handles or track clients; status OK with an empty handle is possible if handler/cache is misconfigured.

## Test Signals
Mount client integration tests should verify handle/auth flavor encoding and non-OK status behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/go-nfs/mount.go -->
