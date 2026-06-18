## sources/user-network-fs/go-fuse/fuse/defaultraw.go

Purpose: null implementation of `RawFileSystem` for embedding by custom filesystems.

Important APIs/types/functions: `NewDefaultRawFileSystem` returns `defaultRawFileSystem`. Methods implement all `RawFileSystem` callbacks, generally returning `ENOSYS`, `EIO`, or no-op success where appropriate, with `String`, `Init`, `OnUnmount`, and `SetDebug`.

Control flow: embedded implementations override selected methods; unimplemented operations receive consistent kernel errors.

State and persistence: stateless singleton-style implementation.

Dependencies and integration: used by tests and user filesystems that want to implement only a subset of raw operations.

Risks and test signals: default status choices influence kernel behavior. For example, `ENOSYS` may disable future kernel calls for some operations, so changes are compatibility-sensitive.
