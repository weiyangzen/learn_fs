<!-- BEGIN_FILE_RESEARCH: sources/test-tools/kdevops/workflows/rcloud/src/metrics.rs -->
# sources/test-tools/kdevops/workflows/rcloud/src/metrics.rs

## Purpose
This module owns rcloud's Prometheus metrics registry and helper methods for request and VM operation counters.

## Important Types and Functions
`ApiLabels` is an encoded label set with `method`, `endpoint`, and `status`. `Metrics` stores an `Arc<Mutex<Registry>>`, a `Family<ApiLabels, Counter>` for HTTP requests, a `Gauge` for VM count, and a `Family<ApiLabels, Counter>` for VM operations. `new()` registers `rcloud_http_requests_total`, `rcloud_vm_count`, and `rcloud_vm_operations_total`. `record_request`, `set_vm_count`, `record_vm_operation`, and `encode` update or serialize metrics.

## Control Flow
Metrics are initialized once in `main.rs` and shared through Actix app data. `/metrics` calls `encode()`, which locks the registry and encodes Prometheus text into a buffer.

## State, Persistence, and Dependencies
Metrics are in-memory only and reset when the service restarts. The module depends on `prometheus-client`, `Arc`, and `Mutex`.

## Risks and Test Signals
The recording helpers are marked dead code and are not wired into request handlers, so counters may stay at zero. Lock failure in `encode()` silently returns an empty buffer. Tests should verify registration output and add integration coverage once handlers record metrics.
<!-- END_FILE_RESEARCH: sources/test-tools/kdevops/workflows/rcloud/src/metrics.rs -->
