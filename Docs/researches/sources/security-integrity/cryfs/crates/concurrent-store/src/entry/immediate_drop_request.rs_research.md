<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/cryfs/crates/concurrent-store/src/entry/immediate_drop_request.rs -->
# sources/security-integrity/cryfs/crates/concurrent-store/src/entry/immediate_drop_request.rs

Purpose: stores and arbitrates an exclusive "immediate drop" request for an entry that is currently loading or loaded.

Important APIs/types/functions: `ImmediateDropRequest<V>` is either `NotRequested` or `Requested { drop_fn, on_dropped }`. `request_immediate_drop_if_not_yet_requested` installs the callback once and returns `Requested`, or returns a shared future for the earlier request. `immediate_drop_requested` exposes the completion `Event`. `ImmediateDropRequestResponse` communicates the two outcomes.

Control flow: when requested, future loads are blocked by `store.rs`; once all active/unfulfilled readers are gone, the store consumes the loaded entry and invokes `drop_fn` with exclusive access. The wrapper triggers `on_dropped` after the callback finishes so blocked tasks can retry.

State and persistence: state is in memory; the `Event` is a one-shot synchronization primitive. The callback owns the actual persistence side effect, such as deleting underlying storage.

Dependencies/integration: requires `AsyncDropGuard<V>`, `Event`, boxed futures, and `Shared`. `EntryStateLoaded` and `EntryStateLoading` embed it.

Risks/test signals: callback is boxed as `dyn FnOnce`; failure handling is left to the callback and store path. Duplicate requests intentionally do not replace the original callback.
<!-- END_FILE_RESEARCH: sources/security-integrity/cryfs/crates/concurrent-store/src/entry/immediate_drop_request.rs -->
