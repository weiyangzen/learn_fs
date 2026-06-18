# sources/storage-engines/tikv/components/engine_traits/src/compaction_job.rs

Purpose: Defines a generic view of backend compaction-job metadata.

Important APIs and control flow: `CompactionJobInfo` exposes job status, CF name, input/output file counts and paths, table-property collection view, input/output levels, elapsed time, corrupt-key count, record counts, byte totals, and backend compaction reason.

State, persistence, and dependencies: It describes a completed or in-flight compaction job and references persistent SST files, but does not mutate state itself.

Integration points, risks, and test signals: Used by event listeners, metrics, and debugging. Risks include backend-specific reason enums, stale file paths after deletion, status conversion loss, and table-property view lifetimes. Java RocksDB tests elsewhere cover similar metadata defaults; this Rust trait has implementor-driven signals.
