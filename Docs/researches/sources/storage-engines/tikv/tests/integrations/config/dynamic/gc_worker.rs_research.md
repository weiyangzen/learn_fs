# sources/storage-engines/tikv/tests/integrations/config/dynamic/gc_worker.rs

## sources/storage-engines/tikv/tests/integrations/config/dynamic/gc_worker.rs

Purpose: verifies validation and online updates for `GcConfig` and the GC worker IO limiter.

Important APIs: `GcConfig::validate`, `GcWorker::new/start`, `GcTask::Validate`, `ConfigController`, `Module::Gc`, `GcWorkerConfigManager`, `Scheduler<GcTask<_>>`, and `Limiter`.

Control flow: `setup_cfg_controller` builds a test Rocks engine, starts a `GcWorker` with a mock region provider, registers its config manager, and returns the scheduler plus controller. `validate` sends a `GcTask::Validate` closure to inspect worker-local config and limiter state. Tests reject `batch_keys = 0`, prove unrelated raftstore updates do not alter GC config, then update ratio, batch keys, write limit, and compaction filter. Separate tests change `gc.max-write-bytes-per-sec` through `ConfigController` and directly through the worker config manager.

State and persistence: state is in worker memory and the limiter. No durable config file is written. The IO limit transitions between infinity and finite byte-per-second speeds.

Dependencies and integration points: TiKV server GC worker, online config controller, test engine builder, raftstore mock region info, and `tikv_util::time::Limiter`. Risks include async scheduling timeouts and float equality for limiter speed. Test signals are closure assertions run inside the GC worker within three seconds.
