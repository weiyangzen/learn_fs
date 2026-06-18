# sources/storage-engines/rocksdb/include/rocksdb/compaction_job_stats.h

## Purpose

`compaction_job_stats.h` defines `CompactionJobStats`, the public aggregate of timing, IO, input/output, blob, deletion, corruption, and key-prefix metrics for a compaction job. It is a plain data carrier with `Reset()` and `Add()` helpers so compaction code can populate per-job stats and listeners/bindings can expose them.

## Important APIs, Types, and Functions

`CompactionJobStats` constructs by calling `Reset()`, provides `Reset()` to clear fields, and `Add(const CompactionJobStats&)` to aggregate another instance. Fields include elapsed wall-clock and CPU microseconds, an accuracy flag for input-record counts, input/output record counts, blob read counts, input/output table and blob file counts, trivially moved and filtered input file counts, full/manual/remote compaction flags, input/output byte totals, skipped input bytes, replaced-record counts, raw key/value bytes, deletion and expired-deletion counts, corrupt key count, optional background IO nanosecond counters, smallest/largest output key prefixes, and single-delete fallthrough/mismatch counters.

`kMaxPrefixLength` is the public maximum for output key prefix strings. The TODO notes missing output-to-proximal-level information.

## Control Flow

This header contains no algorithmic compaction control flow. The compaction engine creates a stats object, records values as the job runs, may aggregate sub-job or remote-worker stats with `Add()`, and reports the final struct to logs, event listeners, Java JNI, or DB internals. `Reset()` supports object reuse and construction initialization.

## State and Persistence Behavior

Stats are in-memory observations about persistent compaction work. They do not directly change database state, but they describe changes to durable table/blob files and compaction side effects. The fields distinguish compaction input from output, bytes skipped by optimizations, blob files read/written, tombstones expired, and corrupt keys encountered and written out. `is_remote_compaction` lets monitoring separate local and remote execution paths.

Accuracy is not absolute. `has_accurate_num_input_records` documents that input record counts can be inaccurate across subcompactions depending on compaction iterator implementation details. Background IO fields are only populated when `options.report_bg_io_stats` is true.

## Dependencies and Integration Points

The header depends on standard size/integer headers, `<string>`, and `rocksdb_namespace.h`. It integrates with compaction execution in `db/compaction/compaction_job.cc`, DB implementation compaction/flush notification paths, event listener compaction info accessors in the C API, Java JNI `CompactionJobStats`, and logging/monitoring surfaces. Search signals show usage in `db_impl_compaction_flush.cc`, `db_impl.h`, Java `rocksjni/compaction_job_stats.cc`, and compaction tests.

## Risks and Edge Cases

Because this struct is public, adding/removing/retyping fields can affect ABI/API users and language bindings. Aggregation must handle booleans, accuracy flags, strings, and optional IO stats carefully; simple numeric addition is not always semantically sufficient. Counter overflow is theoretically possible for very large or long-running workloads. Consumers must respect the accuracy flag and the `report_bg_io_stats` condition rather than treating all zeros as measured zeros.

Remote compaction makes provenance important: aggregating local and remote stats without preserving `is_remote_compaction` can obscure operational behavior. Prefix strings are limited to eight bytes and are not full keys, so diagnostics must not infer exact key ranges solely from them.

## Test Signals

Tests around compaction execution and Java JNI stats access are relevant. Search points to Java `CompactionJobStatsTest`, JNI getters in `java/rocksjni/compaction_job_stats.cc`, and compaction job tests under `db/compaction`. Changes should also be validated through event listener compaction callbacks and options enabling `report_bg_io_stats`.
