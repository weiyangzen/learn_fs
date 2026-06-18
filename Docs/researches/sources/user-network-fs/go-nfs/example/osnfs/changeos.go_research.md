<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-nfs/example/osnfs/changeos.go -->
# sources/user-network-fs/go-nfs/example/osnfs/changeos.go

## Purpose
Adds metadata mutation support to a billy OS filesystem wrapper for the writable NFS example.

## Important APIs, Types, and Functions
`NewChangeOSFS`, `COS`, `Chmod`, `Lchown`, `Chown`, and `Chtimes` are the main APIs.

## Control Flow
Each method joins the billy root with the requested path and delegates to the corresponding `os` package function.

## State and Persistence Behavior
No extra state beyond the embedded billy filesystem.

## Dependencies and Integration Points
Used by `example/osnfs/main.go` through `NullAuthHandler.Change`; integrates with NFS setattr/create/mkdir flows.

## Risks and Edge Cases
Path joining relies on the billy filesystem's root and join behavior; no extra path traversal hardening beyond osfs/chroot semantics.

## Test Signals
Manual NFS setattr/chmod/chown tests against `osnfs` validate these methods.
<!-- END_FILE_RESEARCH: sources/user-network-fs/go-nfs/example/osnfs/changeos.go -->
