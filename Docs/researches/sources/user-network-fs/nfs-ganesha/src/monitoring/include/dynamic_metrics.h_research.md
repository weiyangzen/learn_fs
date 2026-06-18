<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/monitoring/include/dynamic_metrics.h -->
# sources/user-network-fs/nfs-ganesha/src/monitoring/include/dynamic_metrics.h

## Purpose
This header defines the C ABI used by the rest of NFS-Ganesha to initialize and update dynamic monitoring metrics, while compiling to inline no-ops when monitoring is disabled.

## Important APIs, Types, and Functions
It defines `export_id_t` as `uint16_t`. Under `USE_MONITORING`, it declares `dynamic_metrics__init()`, `dynamic_metrics__observe_nfs_request()`, `dynamic_metrics__observe_nfs_io()`, `dynamic_metrics__mdcache_cache_hit()`, `dynamic_metrics__mdcache_cache_miss()`, and optional `dynamic_metrics__mem_info(proc_t proc_info)` when `HAVE_PROCPS` is defined. Request observation accepts operation, elapsed nanoseconds, NFS version, status label, export id, path, and client IP. IO observation accepts requested/transferred byte counts, read/write direction, export id, path, and client IP.

When `USE_MONITORING` is not defined, the same API is provided as static inline no-op functions with unused-argument annotations.

## Control Flow
The header itself has no runtime control flow beyond compile-time selection. C and C++ callers share the declarations through `extern "C"`. Disabled-monitoring builds compile callers without `#ifdef` blocks because every function returns immediately.

## State and Persistence Behavior
No state is stored in the header. Runtime metric state belongs to `dynamic_metrics.cc` and the monitoring registry. Disabled builds persist no metrics.

## Dependencies and Integration Points
The header depends on `config.h`, `gsh_types.h`, `monitoring.h`, standard integer/size/bool headers, and optional procps `proc/readproc.h`. It is included from C and C++ code paths such as request stats and MDCACHE helpers.

## Risks and Edge Cases
The disabled inline `dynamic_metrics__mem_info` signature takes `proc_t *` while the enabled declaration takes `proc_t` by value. That mismatch can matter for code compiled with `HAVE_PROCPS` but without `USE_MONITORING`, depending on caller expectations. The fallback defines an `UNUSED` macro if missing, which can collide with other local conventions. Callers must still pass valid pointers in enabled builds; the API does not encode nullability.

## Test Signals
Build matrix tests should compile with monitoring on/off and procps on/off. ABI tests should ensure C callers link against the C++ implementation when enabled and compile cleanly to no-ops when disabled.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/monitoring/include/dynamic_metrics.h -->
