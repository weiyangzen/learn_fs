<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-nfs/nfs_onreaddir.go -->
# sources/user-network-fs/go-nfs/nfs_onreaddir.go

## Purpose
Implements NFS READDIR with cookie verifier support.

## Important APIs, Types, and Functions
`readDirArgs`, `readDirEntity`, `onReadDir`, `getDirListingWithVerifier`, and local `hashPathAndContents` are central.

## Control Flow
It resolves a directory handle, obtains sorted listing from cache or filesystem, validates cookie verifier, emits `.`/`..` and entries starting after the requested cookie until estimated count or handle-limit thresholds, then writes eof.

## State and Persistence Behavior
No filesystem mutation; verifier/listing caches may be updated through `CachingHandler`.

## Dependencies and Integration Points
Depends on handler handle/verifier interfaces, billy `ReadDir`, sorting, and XDR.

## Risks and Edge Cases
Response sizing uses rough estimates, cookies are index-based and unstable if directory changes, and there is a duplicate hash helper also present in helpers with slightly different input format.

## Test Signals
READDIR tests should cover small count, bad verifier, continuation cookies, changed directories, and handle-limit truncation.
<!-- END_FILE_RESEARCH: sources/user-network-fs/go-nfs/nfs_onreaddir.go -->
