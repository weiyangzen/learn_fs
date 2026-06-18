# sources/storage-engines/tikv/components/raftstore-v2/src/router/imp.rs

Purpose: this file implements adapter traits and router wrappers for raftstore-v2, connecting internal `StoreRouter` to async read notifications, coprocessor split/bucket hooks, local reads, CDC, and unsafe recovery.

Important APIs/types/functions: `AsyncReadNotifier for StoreRouter` forwards fetched logs and generated snapshots to peers. `StoreHandle for StoreRouter` sends approximate-size/key updates, split requests, and bucket refreshes. `RaftRouter` wraps `StoreRouter` and `LocalReader`. `CdcHandle for RaftRouter` implements `capture_change` and `check_leadership`. `UnsafeRecoveryRouter` wraps a mutexed `StoreRouter` and implements `UnsafeRecoveryHandle`.

Control flow: async read callbacks force-send peer messages. StoreHandle methods convert coprocessor signals into `PeerMsg` variants. `RaftRouter::new` creates local store meta for `LocalReader`; `snapshot` delegates read-only snapshot execution to local reader. CDC capture builds an `AnyResChannel` callback that downcasts a region snapshot or forwards an error response. Unsafe recovery methods translate coordinator requests into peer/store messages, using broadcast for exit/wait/report and force/control sends for create/report.

State and persistence: routers do not persist data. They hold router handles, local reader metadata, and callback channels. Unsafe recovery router mutex serializes access to the underlying router object.

Dependencies/integration: depends on raftstore traits `AsyncReadNotifier`, `StoreHandle`, `CdcHandle`, and `UnsafeRecoveryHandle`; uses `PeerMsg`, `StoreMsg`, response channels, `LocalReader`, and `StoreMeta`.

Risks: force-send paths bypass normal backpressure; dropped messages are converted to region-not-found or generic errors inconsistently depending on operation. CDC downcast assumes snapshot type matches `EK::Snapshot`. `UnsafeRecoveryRouter::send_destroy_peer` treats missing region as success because peer may already be gone.

Test signals: no local tests. Coverage is by router trait integration, CDC tests, unsafe recovery tests, and local-read snapshot tests.
