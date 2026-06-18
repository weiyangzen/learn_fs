# sources/storage-engines/rocksdb/util/compaction_job_stats_impl.cc

Purpose: implements reset and aggregation behavior for `CompactionJobStats`, the struct RocksDB uses to report compaction metrics such as timing, record counts, byte counts, file counts, deletion handling, corruption count, write timing, and single-delete anomalies.

Important APIs and functions: `CompactionJobStats::Reset()` sets numeric counters to zero, restores booleans to defaults, sets `has_accurate_num_input_records` true, clears smallest/largest output key prefixes, and resets compaction flags. `CompactionJobStats::Add(const CompactionJobStats&)` accumulates counters, ANDs `has_accurate_num_input_records`, ORs `is_remote_compaction`, and adds file/write timing and single-delete counters.

Control flow and state: state is stored directly in the public stats object. `Reset` is a full reinitialization. `Add` is additive aggregation except for booleans with explicit semantics. Notably `Add` does not aggregate `is_full_compaction`, `is_manual_compaction`, or key prefix strings.

Dependencies and integration: includes `rocksdb/compaction_job_stats.h`. It integrates with compaction job reporting, event listeners, and external stats consumers.

Risks and test signals: aggregation omissions may be intentional for job-level flags, but consumers should not assume all fields are merged. Arithmetic can overflow on long-running or aggregated workloads because fields are plain counters. No direct tests in this subset; coverage is likely indirect through compaction tests and API consumers.
