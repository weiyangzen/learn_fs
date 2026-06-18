<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-nfs/handler.go -->
# sources/user-network-fs/go-nfs/handler.go

## Purpose
Defines the user-supplied filesystem handler interfaces for go-nfs.

## Important APIs, Types, and Functions
`Handler`, `UnixChange`, and `CachingHandler` specify mount authorization, mutation support, handle mapping, FS stats, special-file operations, and directory verifier cache hooks.

## Control Flow
Connection/procedure code calls these interfaces for every request rather than owning a filesystem directly.

## State and Persistence Behavior
Implementations may hold persistent handle caches, mounted filesystems, and authorization state; this file only defines contracts.

## Dependencies and Integration Points
Used by helper handlers, examples, and all NFS procedures.

## Risks and Edge Cases
Incorrect handler implementations can break stateless NFS semantics, leak stale handles, or expose writes without authorization. `HandleLimit` influences readdir chunking.

## Test Signals
Interface conformance is tested indirectly by helpers, examples, and procedure tests.
<!-- END_FILE_RESEARCH: sources/user-network-fs/go-nfs/handler.go -->
