<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-nfs/nfs_onreaddirplus.go -->
# sources/user-network-fs/go-nfs/nfs_onreaddirplus.go

## Purpose
Implements NFS READDIRPLUS with attrs and handles for each directory entry.

## Important APIs, Types, and Functions
`readDirPlusArgs`, `readDirPlusEntity`, `joinPath`, and `onReadDirPlus` are central.

## Control Flow
It mirrors READDIR but also generates attributes and file handles for entries, tracks both `DirCount` and `MaxCount`, and includes post-op attrs and verifier in the response.

## State and Persistence Behavior
May allocate/reuse many cached handles for returned entries; no backing filesystem mutation.

## Dependencies and Integration Points
Depends on `getDirListingWithVerifier`, `Handler.ToHandle`, `ToFileAttribute`, and XDR optional fields.

## Risks and Edge Cases
Sizing is approximate; handle cache limits influence pagination; `.` and `..` do not both include handles/attrs consistently.

## Test Signals
READDIRPLUS tests should cover pagination, verifier reuse, attrs/handles presence, and too-small arguments.
<!-- END_FILE_RESEARCH: sources/user-network-fs/go-nfs/nfs_onreaddirplus.go -->
