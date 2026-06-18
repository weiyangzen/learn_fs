# sources/storage-engines/tikv/components/raftstore-v2/src/operation/unsafe_recovery/create.rs

Purpose: this file creates missing peers during unsafe recovery by reusing raftstore-v2 split initialization, because v2 peers are normally initialized only through snapshots/tablets.

Important APIs/functions: `Store::on_unsafe_recovery_create_peer` performs store-level creation. `Peer::on_unsafe_recovery_wait_initialized` records a wait state, and `unsafe_recovery_maybe_finish_wait_initialized` clears it once storage is initialized or force-finished.

Control flow: the store first checks `StoreMeta.region_ranges` for overlap with the target region. Existing same-region creation becomes a no-op; overlapping different regions aborts. It then creates an empty tablet under `temp_split_path` with tablet index `RAFT_INIT_LOG_INDEX`, constructs a `SplitInit` with no derived region, and calls `on_split_init` with `skip_if_exists`. Finally it force-sends `PeerMsg::UnsafeRecoveryWaitInitialized` to the new region so the peer can hold the execution syncer until initialization finishes.

State and persistence: creation writes an empty temporary tablet through the tablet factory before split initialization. The subsequent split-init path is responsible for moving peer/region state toward initialized status. Peer state stores `UnsafeRecoveryState::WaitInitialize(syncer)` unless a non-aborted unsafe recovery state is already active.

Dependencies/integration: depends on `StoreMeta` range indexes, TiKV key encoding helpers for overlap checks, `TabletRegistry`, `SplitInit`, `PeerPessimisticLocks`, and router force-send. It integrates with unsafe recovery execution syncers from raftstore and with normal split-init peer creation machinery.

Risks: the source TODO notes recovery from abort after opening the temporary tablet is incomplete. The overlap check must be exact, or unsafe recovery could create overlapping peers. If a peer already exists, split-init is skipped because peer FSM cannot process concurrent split-init messages. Syncer lifetime depends on the peer receiving the wait message before being destroyed.

Test signals: no local tests in this file. Coverage should come from unsafe recovery create-peer and split-init integration tests.
