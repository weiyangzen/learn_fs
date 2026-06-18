<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-nfs/nfs_onmknod.go -->
# sources/user-network-fs/go-nfs/nfs_onmknod.go

## Purpose
Implements NFS MKNOD for character devices, block devices, sockets, and FIFOs through `UnixChange`.

## Important APIs, Types, and Functions
`nfs_ftype` constants and `onMknod` are central.

## Control Flow
The handler decodes parent/name/type, resolves and validates parent/write support, obtains `UnixChange`, parses type-specific attrs/specdata, creates the special node, applies attrs, and writes handle, attrs, and WCC.

## State and Persistence Behavior
Persistent state is a special filesystem object in the backing store.

## Dependencies and Integration Points
Depends on `UnixChange.Mknod`, `Mkfifo`, `Socket`, `SetFileAttributes`, and XDR.

## Risks and Edge Cases
The switch groups char and block cases together via empty `case FTYPE_NF3CHR:` fallthrough-like behavior is not automatic in Go, so char devices currently do nothing before success body. Permissions require OS privileges.

## Test Signals
Tests should cover each supported ftype, char-device behavior, bad type, no UnixChange, and unprivileged error mapping.
<!-- END_FILE_RESEARCH: sources/user-network-fs/go-nfs/nfs_onmknod.go -->
