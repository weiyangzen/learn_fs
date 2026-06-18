# sources/sync-backup/kopia/repo/blob/beforeop/beforeop.go

Purpose: provides a wrapper that invokes callbacks immediately before selected blob storage operations.

Important APIs/types/functions: callback types, `beforeOp`, `GetBlob`, `GetMetadata`, `PutBlob`, `DeleteBlob`, `NewWrapper`, and `NewUniformWrapper`. The `onPutBlob` callback receives a pointer to the operation's `PutOptions`, allowing mutation before forwarding.

Control flow: each overridden method checks whether its callback is configured. If present, callback errors short-circuit the underlying operation. Otherwise the operation delegates to the wrapped `blob.Storage`. Uniform wrapper adapts a single callback to all four operations.

State and persistence behavior: the wrapper has no persistence. It can alter write behavior by mutating `PutOptions`, and callbacks may introduce external state or side effects.

Dependencies/integration points: useful for instrumentation, gatekeeping, option injection, or repository-state checks before storage access. Risks include callback side effects, no callbacks for `ListBlobs`, `Close`, `GetCapacity`, or `FlushCaches`, and only value-copy `PutOptions` mutation scoped to that call. Tests cover negative short-circuiting and positive callback invocation/delegation.
