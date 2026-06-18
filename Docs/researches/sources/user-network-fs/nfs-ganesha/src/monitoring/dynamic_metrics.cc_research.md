<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/monitoring/dynamic_metrics.cc -->
# sources/user-network-fs/nfs-ganesha/src/monitoring/dynamic_metrics.cc

## Purpose
This file implements runtime-created Prometheus metrics for NFS-Ganesha when `USE_MONITORING` is enabled. It records per-operation, per-export, per-client, cache hit/miss, memory, swap, and CPU utilization metrics.

## Important APIs, Types, and Functions
The internal `DynamicMetrics` class owns Prometheus family references for counters, gauges, and histograms. Counter families include `mdcache_cache_hits_total`, `mdcache_cache_misses_total`, `rpcs_received_total`, `rpcs_completed_total`, `nfs_errors_total`, client request/byte totals, operation totals, and export-scoped totals. Gauge families include `last_client_update`, `nfs_memory_resident_ram_size`, `nfs_virtual_ram_size`, `nfs_memory_swap_size`, and `nfs_cpu_utilization`. Histogram families include request/response size and latency, both by operation and by operation/export/path.

`requestSizeBuckets` cover 2 bytes through 16 MiB by powers of two. `latencyBuckets` cover roughly 0.1 ms through 12.783 s. `SimpleMap` is a small shared-mutex-protected cache used to turn `export_id_t` into stable strings like `export_id=123`. Utility functions include `trimIPv6Prefix()`, `GetExportLabel()`, and `toLowerCase()`.

Extern "C" entry points are `dynamic_metrics__init()`, `dynamic_metrics__observe_nfs_request()`, `dynamic_metrics__observe_nfs_io()`, `dynamic_metrics__mdcache_cache_hit()`, `dynamic_metrics__mdcache_cache_miss()`, and, with `HAVE_PROCPS`, `dynamic_metrics__mem_info()`.

## Control Flow
`dynamic_metrics__init()` is idempotent via a static boolean. It obtains the global monitoring registry handle from `monitoring__get_registry_handle()`, casts it to `prometheus::Registry *`, and constructs the single `dynamic_metrics` object.

`dynamic_metrics__observe_nfs_request()` returns immediately until initialized. It converts request time from nanoseconds to milliseconds, lowercases the operation label, optionally updates per-client request count and last-update epoch after trimming IPv4-mapped IPv6 prefixes, increments `nfs_errors_total` for every status label, increments total requests by operation, and observes latency by operation. If `export_id` is nonzero, it also updates request count and latency by operation/export/path.

`dynamic_metrics__observe_nfs_io()` maps `is_write` to an operation label and divides bytes into received/sent. It updates optional per-client byte counters, operation-level byte counters and request/response size histograms, then, for nonzero exports, export/path-scoped byte counters and size histograms.

MDCache hit/miss functions increment operation totals and optional export totals. `dynamic_metrics__mem_info()` converts procps `proc_t` memory fields into gauge values and computes process CPU utilization from proc utime/stime, system uptime, process start time, clock ticks, and online CPU count.

## State and Persistence Behavior
Metric families and label children persist in the in-process Prometheus registry for the life of the process. The global `dynamic_metrics` unique pointer is initialized once and is never reset. Label cardinality is dynamic: every new client, operation, status, export, and path combination can create a persistent child metric. `SimpleMap` caches export labels and grows monotonically.

## Dependencies and Integration Points
The file depends on `dynamic_metrics.h`, `monitoring.h`, prometheus-cpp-lite counter/gauge/histogram APIs, C++ STL containers/locks/strings, `nsecs_elapsed_t`, `NS_PER_MSEC`, and optional procps plus Linux `sysinfo()`. Callers are in server statistics and MDCACHE helper paths; the Prometheus exposer scrapes the registry and calls resource updates after scrapes when dynamic metrics are enabled.

## Risks and Edge Cases
Dynamic labels can create high cardinality, especially `client` and `path`. The header warns that dynamic metrics affect performance, and this implementation confirms that risk by retaining all label children for process lifetime. `operation` is lowercased with `::tolower` on `char`; non-ASCII signed char values would be undefined, though NFS operation strings are expected to be ASCII.

`path` is passed directly into export-scoped labels without a null check in the nonzero-export path. `status_label`, `version`, and `operation` are also assumed non-null. `dynamic_metrics__init()` is not protected by a mutex, so concurrent first calls could race on `initialized` and `dynamic_metrics`. Procps resource gauges are compiled under `HAVE_PROCPS`, but `dynamic_metrics__mem_info()` does not check `dynamic_metrics` before dereferencing it; it relies on initialization order.

The counter `errorsByVersionOperationStatus` is incremented for every status, not only failures, despite its metric name/help saying errors. `rpcsReceivedTotal`, `rpcsCompletedTotal`, and `rpcsInFlight` are declared/registered but not updated in this file.

## Test Signals
Tests should verify idempotent initialization, no-op behavior before initialization for most functions, expected metric names/help/labels, operation lowercasing, IPv4-mapped IPv6 client normalization, export id zero suppression, path label creation for nonzero exports, bucket boundaries, cache hit/miss counters, and procps CPU/memory gauge calculations. Stress tests should measure cardinality and lock overhead under many clients/exports/paths.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/monitoring/dynamic_metrics.cc -->
