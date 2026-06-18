# sources/storage-engines/tikv/components/resolved_ts/tests/mod.rs

`tests/mod.rs` defines the shared `TestSuite` used by resolved-ts integration and failpoint tests. It wraps a `Cluster<ServerCluster>`, lazily built `TikvClient` and `ImportSstClient` maps, and a grpc `Environment`. `init` runs `test_util::setup_for_ci` once.

`TestSuite::new` constructs a server cluster, configures lease-read timing, enables resolved-ts, and sets a default 10 ms advance interval. Helper methods start and stop the cluster, schedule endpoint `Task`s through the simulated store's resolved-ts scheduler, apply online config changes for advance interval and memory quota, and build correct request contexts from the current region epoch and leader peer.

KV helpers issue prewrite, commit, and rollback RPCs with assertions that region and key errors are absent. Client helpers create TiKV and import clients for the current region leader. Diagnosis helpers read resolved-ts and tracked indexes from leader store metadata, with retry loops for asynchronous advancement. `must_get_rts` and `must_get_rts_ge` poll up to 50 times with sleeps.

There is no production state here, but it is an integration point into test raftstore internals and resolved-ts task scheduling. Risks are test flakiness due to timing, leader movement, and fixed retry windows. Its presence makes tests concise and consistently validates public behavior through real RPCs rather than only unit-level resolver calls.
