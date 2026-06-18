<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/monitoring/include/prometheus_exposer.h -->
# sources/user-network-fs/nfs-ganesha/src/monitoring/include/prometheus_exposer.h

## Purpose
This header declares the Prometheus HTTP exposer API and, for C++ builds with monitoring enabled, the `ganesha_monitoring::PrometheusExposer` class.

## Important APIs, Types, and Functions
It aliases `sockaddr_t` to `struct sockaddr_storage`. Under `USE_MONITORING`, C callers see `prometheus_exposer__start(const sockaddr_t *addr, uint16_t port, prometheus_registry_handle_t registry_handle)` and `prometheus_exposer__stop(prometheus_registry_handle_t registry_handle)`. C++ callers additionally see `update_mem_info()` and the `PrometheusExposer` class.

`PrometheusExposer` owns a Prometheus registry reference, a scrape-latency histogram family, success/failure scrape histograms, a server socket fd, a running flag, a server thread, and a mutex. Copy and move are deleted.

When monitoring is disabled, the start/stop functions are static inline no-ops.

## Control Flow
Compile-time `USE_MONITORING` and `__cplusplus` select either C declarations, C++ class declarations, or no-op stubs. Runtime behavior is implemented in `prometheus_exposer.cc`.

## State and Persistence Behavior
The header defines the shape of runtime state but does not instantiate it. The class is intended to start and stop a background socket server for the lifetime of monitoring.

## Dependencies and Integration Points
It depends on `monitoring.h` for the registry handle and, in C++ mode, prometheus histogram/text serializer/registry headers plus `<thread>`. It is used by C startup/shutdown paths and by the C++ implementation.

## Risks and Edge Cases
The API accepts a generic `sockaddr_storage` pointer and port; callers must initialize the family and address fields correctly. Disabled-monitoring stubs hide all effects, so integration tests must explicitly include enabled builds. The header exposes `update_mem_info()` in C++ only, but that function depends on procps in the implementation.

## Test Signals
Build tests should cover C and C++ inclusion with monitoring enabled and disabled. API tests should verify start/stop linkage from C and class construction/destruction from C++ when enabled.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/monitoring/include/prometheus_exposer.h -->
