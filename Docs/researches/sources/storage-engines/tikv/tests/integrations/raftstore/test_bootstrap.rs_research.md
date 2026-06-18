# sources/storage-engines/tikv/tests/integrations/raftstore/test_bootstrap.rs

Purpose: tests raftstore bootstrap idempotency, recovery from prepared bootstrap data, API-version switching constraints, and raftstore-v2 flush-before-stop persistence guarantees.

Important APIs and functions: `test_bootstrap_idempotent` starts/restarts clusters around `add_first_region`. `test_node_bootstrap_with_prepared_data` manually constructs a `MultiRaftServer`, RocksDB/raft engines, `SnapManager`, `CoprocessorHost`, `SstImporter`, and store metadata to verify `prepare_bootstrap_cluster` artifacts are cleaned during startup. API switching uses `TikvConfig.storage.set_api_version`. Flush tests send `PeerMsg::FlushBeforeClose` through raftstore-v2 routers and inspect raft engine flushed indexes.

Control flow: the prepared-data test bootstraps PD first, writes local prepare state, asserts prepare keys and region state exist, starts the node, and asserts those records are removed while PD still has one region. API-version tests run clusters with from/to combinations and distinguish TiDB-prefixed data from ordinary data. Flush tests write CF data across split regions, trigger flush-before-close through peer routers, and assert admin flushed indexes or bounded non-flushing with failpoints.

State and persistence: directly inspects `PREPARE_BOOTSTRAP_KEY`, region local state in `CF_RAFT`, RocksDB CF data, raft engine group flushed indexes, and persisted data after node restart. Failpoints control flush thresholds and completion.

Dependencies and integration points: integrates raftstore server bootstrap code, `MultiRaftServer`, engines, raftstore-v2 router messages, TiKV import service, coprocessor host, worker infrastructure, PD test client, and API-version metadata rules.

Risks: this file touches low-level startup internals and can break with bootstrap layout changes. Failpoint state must be cleaned. Flush-before-stop assertions depend on raftstore-v2 internals and CF last-modified/flushed-index accounting.

Test signals: region count remains one after repeated bootstrap, prepare records are absent after restart, invalid API-version switches fail only for non-TiDB data, flush indexes advance sufficiently, and data survives restart when write/lock CF flush ordering is tricky.
