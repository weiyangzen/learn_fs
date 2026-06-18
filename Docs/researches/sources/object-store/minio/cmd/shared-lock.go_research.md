# sources/object-store/minio/cmd/shared-lock.go

Purpose: This file provides a shared namespace-lock helper that continuously acquires an object-layer lock and hands out derived contexts to consumers. It is used when multiple operations need to share a long-lived cluster lock while still respecting caller cancellation and lock-loss events.

Important APIs and types: `sharedLockTimeout` configures dynamic lock acquisition timeout/retry behavior. `sharedLock` wraps a channel of `LockContext`. `backgroundRoutine` acquires and refreshes the lock. `mergeContext` combines a lock context and caller context. `GetLock` returns a merged context/cancel function. `newSharedLock` starts the background routine.

Control flow: The background goroutine repeatedly creates a namespace lock on `minioMetaBucket` and the provided lock name, attempts `GetLock`, and on success enters a loop sending the same `LockContext` to consumers until the parent context is canceled or the lock context is canceled. If the lock is lost, it breaks out and reacquires. `GetLock` receives a lock context from the channel and returns a context canceled when either the lock is lost, caller context is done, or the returned cancel is called.

State and persistence behavior: No durable state is written. Runtime state is the held namespace lock and the unbuffered channel used to distribute lock contexts. Lock persistence/quorum behavior is delegated to the object layer's namespace lock implementation.

Dependencies and integration points: It depends on `ObjectLayer.NewNSLock`, MinIO metadata bucket naming, `LockContext`, and dynamic timeout support. It is a concurrency primitive for code that needs shared access to a cluster-wide lock.

Risks: `GetLock` blocks until the background routine acquires and sends a lock; if the object layer cannot acquire the lock and caller context is already canceled, `GetLock` still waits because it does not select on caller cancellation before receiving. Consumers must call the returned cancel to release merge goroutines. Lock-loss cancellation must be handled by callers.

Test signals: There are no direct tests here. Useful tests would cover acquisition, caller cancellation, lock-context cancellation, reacquisition after lock loss, and blocked acquisition behavior.
