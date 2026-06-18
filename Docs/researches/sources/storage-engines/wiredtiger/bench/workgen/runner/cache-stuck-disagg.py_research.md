# sources/storage-engines/wiredtiger/bench/workgen/runner/cache-stuck-disagg.py

## Purpose
This workgen runner creates a heavy disaggregated-storage workload intended to reproduce or measure cache-stuck behavior with layered/disagg block management, timestamped transactions, and periodic checkpoints.

## Important APIs, Types, and Functions
It imports `runner`, `wiredtiger`, and `workgen`, creates a `Context`, opens a WiredTiger connection with disaggregated/palite extension config, defines a layered table, constructs `Operation`, `Thread`, and `Workload` objects, uses `txn`, and writes latency output through `latency.workload_latency`.

## Control Flow
The script opens a leader disaggregated connection, creates one table, runs an initial populate workload with eight insert threads plus checkpoint threads for about ten million rows, then builds a 900-second run workload with 24 update threads, 8 insert threads, 8 timestamp-lagged read threads, and one checkpoint thread. It sets timestamp advancement/lags, report interval, runs the workload, records elapsed time, writes latency output, and closes the connection.

## State, Persistence, and Dependencies
Persistent state is the workgen home, palite page-log/disaggregated files, populated table data, and `latency.out`. Dependencies include `WT_BUILDDIR` for the palite extension path, the built `workgen` Python module, and substantial disk/time resources.

## Integration Points, Risks, and Test Signals
It integrates disaggregated storage, precise checkpoints, timestamp management, and workload latency reporting. Risks include very large runtime/resource needs, no explicit guard for missing `WT_BUILDDIR`, and assertion-only failure handling. Signals are workload return code zero, elapsed-time prints, and generated latency file.
