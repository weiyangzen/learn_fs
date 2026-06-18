# sources/storage-engines/tikv/tests/integrations/raftstore/test_v1_v2_mixed.rs

Purpose: validates compatibility between legacy raftstore v1 and raftstore v2 tablet snapshots/learners. It proves v1 can receive a v2-generated tablet snapshot and that v1 compatible learners can ingest raft traffic forwarded from v2.

Important APIs and types: `ForwardFactory`/`ForwardFilter` implement raftstore message filtering and rerouting; `generate_snap<EK: KvEngine>` manually builds a `Snapshot`, `RaftSnapshotData`, checkpoint, `RaftMessage`, and `TabletSnapKey`; `send_snap_v2` sends the snapshot over TiKV gRPC; `check_key_in_engine` polls local engines for replicated data.

Control flow: `test_v1_receive_snap_from_v2` starts independent v1/v2 clusters, writes 20 and 5000 keys into a v2 tablet, generates a tablet snapshot, sends it to the v1 store, opens the final receive path as RocksDB, and checks every key. `test_v1_simple_write` creates v1/v2 two-node clusters, adds learners, installs send/receive filters to bridge raft messages between clusters, writes through v2, and verifies data in the v1 learner engine.

State and persistence: the tests inspect persisted tablet checkpoint files, snapshot receive directories, raft metadata, region epochs, and learner engines. Compatibility depends on `TABLET_SNAPSHOT_VERSION`, snapshot metadata, and cross-cluster peer identity assumptions.

Dependencies and integration: `test_raftstore`, `test_raftstore_v2::WrapFactory`, `engine_rocks`, `engine_traits`, `kvproto::tikvpb::TikvClient`, `TabletSnapManager`, and raft message filters.

Risks: manual snapshot construction can drift from production format; filters drain all messages they see; the tests use polling/timing and independent clusters with matched peer IDs.

Test signals: small and large snapshot receipt plus cross-version learner write propagation catch snapshot format, gRPC transfer, and v1 compatible learner regressions.
