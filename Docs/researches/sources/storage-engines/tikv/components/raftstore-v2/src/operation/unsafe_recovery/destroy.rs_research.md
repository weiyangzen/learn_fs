# sources/storage-engines/tikv/components/raftstore-v2/src/operation/unsafe_recovery/destroy.rs

Purpose: this small file initiates peer destruction as an unsafe recovery plan action.

Important API/function: `Peer::on_unsafe_recovery_destroy_peer(syncer)` validates unsafe recovery state and marks the peer for destruction.

Control flow: if another non-aborted unsafe recovery state exists, it logs a warning, aborts the incoming syncer, and returns. Otherwise it stores `UnsafeRecoveryState::Destroy(syncer)` and calls `mark_for_destroy(None)`. The syncer is intentionally retained in peer state until the normal destroy path completes and drops it.

State and persistence: this file does not directly write storage; it triggers existing peer destroy machinery. The state marker is important because the recovery coordinator is synchronized by the syncer lifetime.

Dependencies/integration: depends on `UnsafeRecoveryExecutePlanSyncer`, `UnsafeRecoveryState`, and peer lifecycle methods from other operation modules.

Risks: if destroy progress does not drop the state/syncer, unsafe recovery execution can hang. Concurrent plan handling is intentionally strict; only aborted states permit replacement.

Test signals: no local tests. Expected coverage is unsafe recovery destroy-plan integration.
