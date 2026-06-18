
# sources/user-network-fs/rclone/fstest/mockfs/mockfs.go

Purpose: package `mockfs` defines a minimal in-memory `fs.Fs` implementation for unit tests that need a registered rclone backend-like object without remote I/O.

Important APIs/types/functions: `Register` registers backend name `mockfs` with one required `potato` option. `Fs` stores `name`, `root`, filled `features`, a root-only `fs.DirEntries` listing, and supported `hash.Set`. `NewFs` constructs it. `AddObject`, `SetHashes`, `List`, and `NewObject` are the functional test hooks. `Put`, `Mkdir`, and `Rmdir` deliberately return `ErrNotImplemented`.

Control flow: `NewFs` fills features from the concrete object. `AddObject` appends to `rootDir` and calls a test-only `SetFs(fs.Fs)` method on the object if present. `List` only succeeds for root. `NewObject` only searches objects directly under root and returns `fs.ErrorObjectNotFound` otherwise.

State/persistence: all state is process-local memory on the `Fs` instance. There is no locking; callers should treat it as a simple single-test fixture.

Dependencies/integration: uses rclone `fs`, `configmap`, and `hash`. It pairs naturally with `mockobject.ContentMockObject`, which can accept the owning Fs through `SetFs`.

Risks: root-only behavior and unimplemented mutations mean it is not a full fake backend. Type assertion in `NewObject` assumes matching entries are `fs.Object`, not directories.

Test signals: compile-time assertion `var _ fs.Fs = (*Fs)(nil)` verifies interface completeness for core methods; behavior is validated indirectly by unit tests using this mock.
