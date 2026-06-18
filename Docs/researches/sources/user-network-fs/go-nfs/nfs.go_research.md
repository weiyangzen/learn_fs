<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-nfs/nfs.go -->
# sources/user-network-fs/go-nfs/nfs.go

## Purpose
Registers all NFSv3 procedure handlers and implements the null procedure.

## Important APIs, Types, and Functions
`init` calls `RegisterMessageHandler` for NFS procedures 0 through 21; `onNull` writes an empty successful response.

## Control Flow
At package initialization, handlers become available to the server dispatch table; null requests return no body.

## State and Persistence Behavior
State is global registration in the server handler registry defined elsewhere in the package.

## Dependencies and Integration Points
Integrates every `nfs_on*.go` handler with `conn.handle`.

## Risks and Edge Cases
Missing or duplicate registration would make procedures unavailable. Registration errors are intentionally ignored with `_ =`.

## Test Signals
Protocol tests should assert all expected NFS procedures are registered and null returns success.
<!-- END_FILE_RESEARCH: sources/user-network-fs/go-nfs/nfs.go -->
