# sources/object-store/rustfs/crates/obs/src/metrics/stats_collector.rs

## Purpose
Implements the sampling and transformation bridge between RustFS runtime/storage/system sources and the DTO structs consumed by metrics collectors. Unlike schema files, this module contains active runtime logic, fallback paths, warnings, and testable helper behavior.

## Important APIs, Types, and Functions
Public collection functions include `collect_cluster_and_health_stats`, `collect_cluster_stats`, `collect_cluster_health_stats`, `collect_bucket_stats`, `collect_bucket_replication_bandwidth_stats`, `collect_bucket_replication_detail_stats`, `collect_replication_stats`, `collect_disk_stats`, `collect_system_cpu_and_memory_stats`, `collect_system_cpu_and_memory_stats_with`, `collect_system_cpu_stats`, `collect_system_memory_stats`, `collect_disk_and_system_drive_stats`, `collect_system_drive_stats`, `collect_process_metric_bundle`, `collect_process_resource_and_system_stats`, `collect_process_stats`, `collect_process_system_stats`, `collect_host_network_stats`, `collect_internode_network_stats`, `collect_cluster_config_stats`, `collect_erasure_set_stats`, `collect_iam_stats`, `collect_cluster_usage_metric_stats`, `collect_ilm_metric_stats`, and `collect_scanner_metric_stats`. Important helpers include `disk_is_online_for_metrics`, `disk_capacity_observation_state`, `derive_erasure_set_quorum_shape`, `apply_erasure_set_health`, scanner mode/rate helpers, and `ProcessMetricBundle`.

## Control Flow
Most collectors resolve a global object store or runtime singleton, return defaults/empty values when unavailable, then map external snapshots into collector DTOs. Storage-based collectors use `StorageAdminApi::storage_info()` or `backend_info()`. Usage collectors load persisted data-usage snapshots and optionally fall back to bucket listing. Replication collectors read `GLOBAL_REPLICATION_STATS`. System collectors use `sysinfo` and `rustfs_io_metrics`. Scanner and ILM collectors read `global_metrics()` and lifecycle globals.

## State and Persistence
The module owns no long-lived mutable state, but it reads persisted data usage from the backend and quota configuration from bucket metadata. It also reads process-lifetime global counters for replication, lifecycle, scanner, internode networking, and IAM. Many failures are converted to empty/default stats and logged with structured `warn!` events rather than propagated.

## Dependencies and Integration Points
This file is a central integration point for `rustfs_ecstore`, `rustfs_storage_api`, `rustfs_iam`, `rustfs_common::metrics`, `rustfs_io_metrics`, `sysinfo`, `chrono`, tracing, and all collector stats structs. Collectors call these functions to obtain data and then apply schema descriptors.

## Risks
Default-on-error behavior can make unavailable data look like zero unless collectors or dashboards expose scrape health separately. Some system fields are placeholders due to source limitations. Online drive classification is policy-heavy and must match operational expectations. Usage metrics depend on stored snapshots and do not trigger rescans. Label and field semantics must stay aligned with schema files and collectors.

## Test Signals
The module has focused unit tests for drive online classification, erasure quorum derivation, health application, scanner cycle age, scan-mode mapping, bucket-scan started fallback, and rate calculation. Integration tests are still needed for storage/IAM/replication/global metric availability and failure logging paths.
