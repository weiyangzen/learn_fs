# sources/object-store/rustfs/crates/obs/src/metrics/collectors/system_gpu.rs

Purpose: optional GPU collector for process GPU memory usage through NVML. It is feature-gated in `collectors/mod.rs` and used by scheduler only under `#[cfg(feature = "gpu")]`.

Important APIs/types: `GpuStats`, `GpuError`, `GpuCollector`, `GpuCollector::new`, `GpuCollector::collect`, and `collect_gpu_metrics`. `GpuError` uses `thiserror::Error` for init/device/process-not-found variants.

Control flow: `new` initializes NVML and stores the monitored PID. `collect` reads device index 0, iterates running compute processes, returns memory bytes for matching PID, maps unavailable memory to 0, logs a warning if process stats are unavailable, returns device error when no GPU device is found, and otherwise returns zero usage when the process is not listed. `collect_gpu_metrics` emits one process GPU memory metric with caller labels.

State/persistence: stores an NVML handle and PID inside `GpuCollector`; no persistent files.

Dependencies/integration: depends on `nvml_wrapper`, `sysinfo::Pid`, `tracing`, and `schema::system_gpu`. Scheduler initializes the collector inside each system interval pass, which may be expensive but isolates failures.

Risks: only device index 0 is inspected, so multi-GPU processes may be underreported. NVML availability and permissions can fail. `ProcessNotFound` exists but current `collect` returns zero instead of that error for absent process.

Test signals: tests cover default stats and display formatting for all error variants, but not real NVML collection.
