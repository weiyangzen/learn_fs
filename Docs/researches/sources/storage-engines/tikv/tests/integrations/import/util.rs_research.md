# sources/storage-engines/tikv/tests/integrations/import/util.rs

Purpose: provides shared setup for ImportSST integration tests. It creates one-node TiKV server clusters, prepares a valid `kvrpcpb::Context`, and opens paired `TikvClient` and `ImportSstClient` gRPC clients.

Important APIs and functions: `new_cluster` and `new_cluster_v2` instantiate raftstore-v1 and raftstore-v2 server clusters, run them, discover leader/epoch for region 1, and return a request context. `open_cluster_and_tikv_import_client` and `_v2` apply default import-test config, create a gRPC channel with keepalive settings and optional TLS credentials, then construct both clients on the same channel. `new_cluster_and_tikv_import_client` is the default convenience wrapper. `new_cluster_and_tikv_import_client_tde` creates a temporary encryption config and returns the tempdir to keep key material alive for the cluster lifetime.

Control flow: caller-provided config is used as-is, otherwise defaults bind the server to `127.0.0.1:0`, reduce cleanup interval to 10 ms, set gRPC concurrency to one, and for v1 enable compaction guard on default/write CFs. Channel construction selects secure or insecure connect based on whether `cfg.security` is default.

State and persistence: cluster engines, import directories, and encrypted storage state are created by the test cluster harness. The returned `Context` carries region id, peer, and epoch, so later ingest calls can pass region validation. TDE setup persists key material in a temporary directory that must outlive the test.

Dependencies and integration points: integrates `test_raftstore`, `test_raftstore_v2`, `engine_rocks::RocksEngine`, `grpcio`, `security`, TiKV config, `HandyRwLock`, and generated kvproto clients.

Risks: the helpers assume a single initial region id of 1 and a one-node cluster, so tests needing split or multi-peer semantics must mutate the cluster afterward. Security comparison against `SecurityConfig::default()` determines TLS setup; partial security config changes must be valid.

Test signals: downstream tests signal setup correctness by successfully connecting to server address from the simulator registry, finding a leader peer, and making import/kv RPCs with the returned context.
