# sources/object-store/rustfs/crates/obs/src/metrics/schema/system_gpu.rs

## Purpose
Defines the GPU memory usage metric descriptor for the RustFS process.

## Important APIs, Types, and Functions
Exports `PROCESS_GPU_MEMORY_USAGE_MD`, a no-label gauge using `MetricName::ProcessGpuMemoryUsage` under `subsystems::SYSTEM_GPU`.

## Control Flow
Lazy descriptor initialization only.

## State and Persistence
No values or persistence. Values are sampled by the GPU collector, which integrates with platform-specific GPU discovery.

## Dependencies and Integration Points
Used by `metrics/collectors/system_gpu.rs`. The metric name composes under `rustfs_system_gpu_gpu_memory_usage`.

## Risks
GPU availability is platform and driver dependent. A no-label descriptor cannot distinguish multiple GPUs. Missing GPU data should be handled by the collector rather than this schema.

## Test Signals
No schema tests. GPU collector tests or platform-gated integration tests are the relevant coverage.
