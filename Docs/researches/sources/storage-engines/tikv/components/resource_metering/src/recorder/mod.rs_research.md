## sources/storage-engines/tikv/components/resource_metering/src/recorder/mod.rs

Purpose: owns the resource metering recorder worker. It drives a vector of `SubRecorder`s at a fixed 99 Hz timer, receives thread/collector/config registration tasks, and periodically emits `RawRecords` to registered collectors.

Important APIs/types/functions: `Recorder`, `RecorderBuilder`, `Task`, `ConfigChangeNotifier`, and `init_recorder`. The module also re-exports collector registration handles, local storage, `CpuRecorder`, `SummaryRecorder`, and the public summary counter functions. `Recorder::tick` runs each sub-recorder’s `tick`, then calls `collect` once the configured precision window elapses. `pause`, `resume`, and `cleanup` bracket active collection and remove dead-thread state.

Control flow: the worker handles `CollectorReg`, `ThreadReg`, and `ConfigChange` tasks through `Runnable::run`; timer ticks call `on_timeout`. If no non-observer collectors are present, the recorder pauses and observers alone do not keep sampling active. When resumed, records and timestamps reset before sub-recorders resume.

State/persistence: state is in-memory only: `RawRecords`, per-thread `LocalStorage`, collector maps, observer maps, and timing instants. Cleanup checks live OS thread ids, shrinks oversized record capacity, and delegates cleanup to sub-recorders. No durable persistence is performed.

Dependencies/integration: uses `tikv_util::worker`, thread ids/stats, `ResourceTagFactory`, resource metering config, and the global `ENABLE_NETWORK_IO_COLLECTION` flag. `init_recorder` is consumed by the server startup path and returns the handles needed by storage, reporter, and config management.

Risks: record delivery is best-effort through worker scheduling; dead thread cleanup depends on platform thread id discovery; observers are intentionally passive; CPU/summary precision depends on timer scheduling. A high `records.records` churn pattern can allocate until periodic shrink.

Test signals: inline tests cover pause/resume, thread registration, collector/observer semantics, record dispatch, and deregistration behavior.
