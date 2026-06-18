# sources/storage-engines/tikv/tests/benches/raftstore/mod.rs

Purpose: Criterion benchmark binary for raftstore set/get/delete operations over node and server cluster simulators.

Important APIs and functions: `enc_write_kvs` directly writes data keys into RocksDB. `prepare_cluster` runs the cluster, seeds initial data into all KV engines, and resolves the leader. `bench_set`, `bench_get`, and `bench_delete` build clusters and measure `must_put`, `get`, and `must_delete`. `bench_raft_cluster` sweeps node counts `1,3,5` and value sizes `8,128,1024,4096`. `ClusterFactory` abstracts `NodeClusterFactory` and `ServerClusterFactory`. `main` checks file descriptors and runs Criterion sample size 10.

Control flow: each benchmark input builds a fresh cluster; get/delete cases preload 100,000 KVs and then mix existing and generated keys.

State and persistence: clusters write to test RocksDB engines. Direct preload bypasses raft for setup; measured operations go through raftstore APIs.

Dependencies and integration: uses Criterion, `test_raftstore`, `test_util::KvGenerator`, Rocks engine traits, and TiKV config fd checking.

Risks and test signals: setup cost is outside timing but cluster lifecycle may still be heavy. Signals raftstore API latency under simulator variants and replica counts.
