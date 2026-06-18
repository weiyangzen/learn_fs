# sources/user-network-fs/rclone/backend/shade/api/types.go

Purpose: JSON data transfer types for the Shade backend.

Important APIs/types/functions: `ListDirResponse` models file/directory attributes returned by Shade FS list and attr endpoints, including type, path, inode, millisecond timestamps, size, hash, and draft flag. `PartURL` models a presigned multipart part upload URL plus optional required headers. `CompletedPart` records ETag and part number for multipart completion.

Control flow: no behavior. `shade.go` consumes `ListDirResponse` for `List`, `NewObject`, root file detection, and directory existence checks. `upload.go` consumes `PartURL` and `CompletedPart` during multipart upload.

State and persistence behavior: none; these are transient JSON payload structures.

Dependencies/integration: package `api` is imported by `shade.go` and `upload.go`.

Risks/test signals: JSON field names must match Shade API. `CompletedPart` lacks explicit JSON tags, relying on Go field names (`ETag`, `PartNumber`) matching the expected completion body. Integration tests are the main validation signal.
