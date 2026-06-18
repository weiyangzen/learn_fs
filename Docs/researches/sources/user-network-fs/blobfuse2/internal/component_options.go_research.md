## sources/user-network-fs/blobfuse2/internal/component_options.go

Purpose: Defines typed option payloads passed through the `Component` interface, plus directory-name helper functions.

Important APIs: Option structs cover directory creation/deletion/listing/renaming, file create/open/read/write/truncate/copy/flush/release/rename, symlink create/read, attributes, chmod/chown, sync, staged block upload, commit, and committed block metadata. `ReadInBufferOptions` supports both handle-based and path/size-based reads, used by xload. `CommitDataOptions` carries block id order, block size, and optional new ETag. `TruncateDirName` removes one trailing slash; `ExtendDirName` adds one trailing slash or returns `/` for empty input.

State and dependencies: The file has no mutable state. It imports `os` and `handlemap`.

Integration points: These structs are the shared ABI between libfuse, xload, loopback, storage backends, and external aliases.

Risks: Option semantics are implicit; for example `BlockSize` zero in `CommitDataOptions` can be harmful if implementations do not default it. Tests cover only `TruncateDirName` and `ExtendDirName`.
