<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-nfs/file/file_wasm.go -->
# sources/user-network-fs/go-nfs/file/file_wasm.go

## Purpose
Extracts wasm-compatible stat metadata where major/minor device numbers are unavailable.

## Important APIs, Types, and Functions
`getOSFileInfo` maps nlink, uid, gid, and inode into `FileInfo`.

## Control Flow
Same flow as the Unix extractor but omits specdata.

## State and Persistence Behavior
Stateless.

## Dependencies and Integration Points
Used by wasm builds of go-nfs metadata conversion.

## Risks and Edge Cases
Wasm filesystem semantics may not provide meaningful inode or ownership values.

## Test Signals
Wasm compilation and simple stat conversion tests validate it.
<!-- END_FILE_RESEARCH: sources/user-network-fs/go-nfs/file/file_wasm.go -->
