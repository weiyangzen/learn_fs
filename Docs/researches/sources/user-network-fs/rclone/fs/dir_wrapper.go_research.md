<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fs/dir_wrapper.go -->
# sources/user-network-fs/rclone/fs/dir_wrapper.go

## Purpose
Wraps a backend `Directory` while overriding its remote path and forwarding optional directory capabilities.

## Important APIs, Types, And Control Flow
`NewDirWrapper` and `NewLimitedDirWrapper` create wrappers; limited wrappers silently ignore missing `SetMetadata` and `SetModTime`. `Remote`, `String`, and `SetRemote` use the override. `Metadata`, `SetMetadata`, and `SetModTime` type-assert optional interfaces and return nil or `ErrorNotImplemented` when unsupported.

## State And Persistence
In-memory wrapper state consists of the wrapped directory, override remote, and fail-silently flag. Persistence is delegated to the wrapped directory's optional methods.

## Dependencies And Integration Points
Implements `DirEntry`, `Directory`, and `FullDirectory`, supporting overlay/combine backends that rewrite paths.

## Risks And Test Signals
Silent failure mode can hide unsupported metadata/modtime changes by design. Compile-time interface checks exist; direct behavior tests are not in this subset.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fs/dir_wrapper.go -->
