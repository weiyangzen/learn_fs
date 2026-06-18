# sources/test-tools/xfstests-bld/test-appliance/files/usr/local/lib/gce-server/ltm/mock.go

Purpose: JSON dump/load and mock execution support for LTM sharder state.

Important types: `JsonSharder` and `JsonShard` mirror selected `ShardScheduler` and `ShardWorker` fields for serialization. Methods `Dump`, `ShardWorker.Dump`, `JsonShard.Read`, and `ReadSharder` round-trip state. `MockNewShardScheduler` and `MockRun` avoid actual VM launches.

State and dependencies: reads/writes JSON files, reconstructs a GCP service in `ReadSharder`, and initializes logs through `logging.InitLogger`. Mock run may forward KCS bisect step callbacks.

Integration points: useful for development, reproducing sharder command construction, and testing LTM/KCS control flow without launching GCE VMs when `logging.MOCK` is true.

Risks and test signals: JSON read/write errors are ignored in this file, so malformed mocks can produce zero-valued sharders. Mock mode does not exercise quota selection, VM monitoring, result aggregation, or GCS cleanup.
