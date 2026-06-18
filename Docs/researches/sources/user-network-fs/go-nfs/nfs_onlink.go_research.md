<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-nfs/nfs_onlink.go -->
# sources/user-network-fs/go-nfs/nfs_onlink.go

## Purpose
Implements NFS LINK for filesystems whose `Change` object supports `UnixChange`.

## Important APIs, Types, and Functions
`onLink` is the handler.

## Control Flow
It decodes a target directory/name, attributes, and source opaque data, resolves parent, validates write capability/name/nonexistence/parent directory, obtains `UnixChange`, calls `Link`, applies attrs, and returns handle, attrs, and WCC.

## State and Persistence Behavior
Persistent state is a new hard link and possible metadata changes.

## Dependencies and Integration Points
Depends on `UnixChange.Link`, `SetFileAttributes`, and handle caching.

## Risks and Edge Cases
The source is decoded as opaque bytes and cast to string path; this may not match NFS LINK argument semantics, where source is usually a file handle. Error mappings are broad.

## Test Signals
Hard-link integration tests against `example/osnfs` should validate source semantics and link counts.
<!-- END_FILE_RESEARCH: sources/user-network-fs/go-nfs/nfs_onlink.go -->
