<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/bench/workgen/runner/compress_ratio.py -->
# sources/storage-engines/wiredtiger/bench/workgen/runner/compress_ratio.py

Purpose: compares update-heavy behavior across several WiredTiger block compressors and zlib page-image configurations. It creates one table per compression option, populates each with compressible values, then runs inserts and updates so statistics logs can reveal compression ratio and performance differences.

Important APIs and functions: defines local `op_append`, `make_op`, and `operations` helpers. `operations` builds an operation list across tables, optionally adding log-table operations and wrapping groups in transactions. It uses `Context`, `Table`, `Key`, `Value`, `Operation`, `Thread`, `Workload`, and Workgen throttling/name options.

Control flow: open a 2 GB cache connection with checkpoint/statistics logging and disabled WT logging; define compressor configs for none, lz4, snappy, zlib, zlib with one-page or ten-page `memory_page_image_max`, and zstd; create a table per compressor; set `value_compressibility=70`; populate 500,000 append-key rows per operation sequence; run two insert threads and ten update threads for 60 seconds with per-thread throttle 1000 and 1-second reporting.

State and persistence: creates persistent table files in the Workgen home. Checkpoints run every 20 seconds from connection config. No explicit latency file is written; the primary persistence artifacts are WiredTiger tables and statistics logs.

Dependencies and integration: requires the configured WiredTiger library to support the listed compressors. The comments note `extensions_config` can be used for externally built compressors, though this script leaves it commented.

Risks: compressor availability is build-dependent and unsupported compressor names fail during `create`. Local helper code duplicates `runner.core` concepts. Workload sizes and throttles are machine-tuned and can overwhelm smaller hosts. No cleanup or final close is present, relying on process exit.

Test signals: `assert ret == 0` after populate and workload, plus WiredTiger JSON statistics log for file sizes/compression counters.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/bench/workgen/runner/compress_ratio.py -->
