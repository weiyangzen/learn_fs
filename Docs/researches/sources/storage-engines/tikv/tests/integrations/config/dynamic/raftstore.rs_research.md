# sources/storage-engines/tikv/tests/integrations/config/dynamic/raftstore.rs

## sources/storage-engines/tikv/tests/integrations/config/dynamic/raftstore.rs

Purpose: exercises raftstore online configuration dispatch into a live raft batch system, including validation boundaries and async IO resizing constraints.

Important APIs: `create_raft_batch_system`, `RaftstoreConfigManager`, `VersionTrack<Config>`, `StoreMsg::Validate`, `RaftRouter`, `ApplyRouter`, `ConfigController`, `Module::Raftstore`, `Engines<RocksEngine, RocksEngine>`, `SnapManager`, `SstImporter`, and `MockTransport`.

Control flow: `start_raftstore` creates temporary Rocks engines, importer, snap manager, store meta, PD worker, split scheduler, and starts the raft batch system. The config manager uses the system refresh scheduler and shared `VersionTrack`. `validate_store` sends a control message through the raft router to inspect live store config. Tests update batch sizes, raft log GC threshold, message size, entry size, yield write size, and snap wait duration; then they try invalid minimum/maximum values and assert live config remains unchanged. IO tests reject switching between sync and async store IO modes while allowing resizing within async mode.

State and persistence: temporary RocksDB directories, raftstore worker threads, and shared `VersionTrack` hold state. Shutdown is explicit per scenario.

Dependencies and integration points: raftstore FSM, PD client, importer, snap manager, health/resource metering/service manager dummies. Risks include broad fixture construction, `MockTransport` panicking if unexpected sends occur, and validation sensitivity to raftstore constraints. Test signals are successful control-message config equality and expected update errors.
