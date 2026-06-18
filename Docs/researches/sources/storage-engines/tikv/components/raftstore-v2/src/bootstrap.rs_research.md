# sources/storage-engines/tikv/components/raftstore-v2/src/bootstrap.rs

Purpose: Implements re-entrant store and first-region bootstrap logic for raftstore-v2. It allocates IDs through PD, writes store identity and initial region state to the raft engine, and coordinates first-region registration with PD.

Important APIs/types/functions: `Bootstrap<'a, ER>` holds a raft engine reference, cluster id, PD client trait object, and logger. `bootstrap_store` validates existing store identity, checks engine emptiness, allocates a store id, writes `StoreIdent`, and syncs the raft log batch. `bootstrap_first_region` resumes any prepared region, checks if PD is already bootstrapped, prepares initial region state, calls `bootstrap_cluster`, and clears preparation markers. Helpers include `check_store_id_in_engine`, `prepare_bootstrap_first_region`, `check_pd_first_region_bootstrapped`, and `clear_prepare_bootstrap`.

Control flow: Store bootstrap is idempotent: if `StoreIdent` exists and cluster id matches, it returns the existing store id. First-region bootstrap writes a prepare marker before contacting PD so failures can resume. If PD reports another first region, the local prepared state is cleaned. If PD reports the same region, this node treats the previous attempt as successful and clears the marker.

State and persistence behavior: Persistent state is written through `RaftLogBatch`: store ident, prepare-bootstrap region marker, initial region state, and raft local/apply state via `write_initial_states`. Cleanup removes the prepare marker and optionally cleans the prepared region's raft state. All bootstrap writes use `sync=true`.

Dependencies and integration points: It uses `engine_traits::RaftEngine`, `pd_client::PdClient`, `raftstore::store::initial_region`, `operation::write_initial_states`, failpoints, and raft server protobufs. It is used before starting the raftstore-v2 batch system.

Risks: Blocking sleeps retry PD checks for up to 60 * 3 seconds. Cluster-id mismatch is fatal to protect against joining a wrong cluster. Failures between local prepare and PD registration rely on correct marker recovery. Concurrent bootstrap is explicitly not thread safe; methods take `&mut self` to discourage it.

Test signals: Failpoints cover after store bootstrap, after prepare bootstrap, and after PD cluster bootstrap. Integration tests should exercise idempotency, competing bootstrap nodes, existing store identity, dirty non-empty engine, and prepare-marker cleanup.
