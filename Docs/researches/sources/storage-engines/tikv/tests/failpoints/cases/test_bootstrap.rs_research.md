# sources/storage-engines/tikv/tests/failpoints/cases/test_bootstrap.rs

Purpose: verifies node bootstrap recovery after injected failures at different bootstrap phases.

Important APIs and functions: helper `test_bootstrap_half_way_failure` drives `NodeCluster` startup with failpoints `node_after_bootstrap_store`, `node_after_prepare_bootstrap_cluster`, and `node_after_bootstrap_cluster`. It inspects `STORE_IDENT_KEY`, calls `set_bootstrapped`, restarts, checks `PREPARE_BOOTSTRAP_KEY`, and validates replication.

Control flow: first `cluster.start()` must fail after partial persistent state. The test then marks the discovered store bootstrapped in PD, removes the failpoint, starts successfully, and writes `k1`.

State and persistence: persistent store identity and prepare-bootstrap keys are the core state. The test asserts stale prepare-bootstrap metadata is cleared.

Dependencies and integration: uses `TestPdClient`, raftstore cluster APIs, engine `Peekable`, and protobuf metapb/raft_serverpb messages.

Risks and test signals: directly manipulates PD bootstrap state, so helper behavior must match production bootstrap contracts. Signal is idempotent restart after partial bootstrap.
