<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/serve/s3/utils.go -->
# sources/user-network-fs/rclone/cmd/serve/s3/utils.go

Source read: complete file, 139 lines, 2676 bytes, sha256 `50055f971d6f2e846bde1e60141553823cd485c1bcc35a4e2ad26b5d7cb1526e`. Final split target: `Docs/researches/sources/user-network-fs/rclone/cmd/serve/s3/utils.go_research.md`.

## Purpose
Contains helper functions for S3 path, hash, directory, cleanup, and auth-pair handling.

## Important APIs, types, and functions
`getDirEntries`, `getFileHashByte`, `getFileHash`, `prefixParser`, `mkdirRecursive`, `rmdirRecursive`, and `authlistResolver` are package helpers used by backend/list/server code.

## Control flow
Directory helpers stat/read VFS nodes, create missing parent chains, and remove empty parent directories recursively. Hash helpers prefer `fs.Object.Hash` but can read VFS cache contents when an upload is still represented by a VFS node without an object entry.

## State and persistence behavior
No durable state. It reads or mutates remote directory structure through VFS mkdir/remove operations.

## Dependencies and integration points
Depends on VFS, gofakes3 errors, rclone hash/multihasher, path/string helpers, and `fs.Object`.

## Risks and edge cases
`mkdirRecursive` uses absolute-looking path construction after trimming and may be sensitive to VFS path conventions. `rmdirRecursive` is intentionally opportunistic and can remove empty parents after object delete. Hashing uploading VFS nodes can be expensive.

## Test signals
Covered indirectly by S3 object operations, listing, upload, and auth tests.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/serve/s3/utils.go -->
