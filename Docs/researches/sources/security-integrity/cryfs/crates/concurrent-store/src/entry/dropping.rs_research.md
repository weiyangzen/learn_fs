<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/concurrent-store/src/entry/dropping.rs -->
# sources/security-integrity/cryfs/crates/concurrent-store/src/entry/dropping.rs

Purpose: represents the `Dropping` state of a concurrent-store entry while an asynchronous drop or immediate-drop callback is in progress.

Important APIs/types/functions: `EntryStateDropping` wraps a `Shared<BoxFuture<'static, ()>>`. `new` stores a real drop future, `new_dummy` creates an already-ready placeholder for temporary state replacement, `future` borrows the shared future, and `into_future` consumes the state.

Control flow: `store.rs` inserts this state when the last loaded guard is released or when an immediate drop is requested for an unloaded key. Callers that find a `Dropping` entry clone and await the shared future outside the entries mutex before retrying.

State and persistence: in-memory only. The shared future is the synchronization point that keeps future loaders from entering until cleanup/removal completes.

Dependencies/integration: uses `futures::FutureExt` and `Shared`. It is re-exported by `entry/mod.rs` and consumed by `ConcurrentStoreInner`.

Risks/test signals: the dummy constructor is safe only as a short-lived replacement before the real future is installed. If a dropping future is not driven to completion, the map can remain blocked for that key.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/concurrent-store/src/entry/dropping.rs -->
