<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/concurrent-store/src/entry/loaded.rs -->
# sources/security-integrity/cryfs/crates/concurrent-store/src/entry/loaded.rs

Purpose: models a successfully loaded entry and tracks live access for unload/drop decisions.

Important APIs/types/functions: `EntryStateLoaded<V>` holds an `AsyncDropArc<V>`, `num_unfulfilled_waiters`, and `ImmediateDropRequest<V>`. Constructors handle just-finished loading and direct insertion. `get_entry` clones access; `get_entry_and_decrease_num_unfulfilled_waiters` finalizes a loading waiter; `num_tasks_with_access` combines unfulfilled waiters plus strong-count minus the map's own reference; `into_inner` extracts the value only when no unfulfilled waiters remain.

Control flow: after loading completes, `store.rs` replaces `EntryStateLoading` with this state and initializes waiter count from the loading state. Dropping starts only when no active or unfulfilled access remains.

State and persistence: in-memory reference accounting only. Immediate-drop callback may later perform persistence-level removal.

Dependencies/integration: uses `AsyncDropArc`, `AsyncDropGuard`, `Event`, and immediate-drop helpers. It is the bridge between shared access guards and exclusive drop.

Risks/test signals: strong-count arithmetic is subtle; leaked or cancelled waiters can keep entries alive. Assertions protect impossible extraction with pending waiters.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/concurrent-store/src/entry/loaded.rs -->
