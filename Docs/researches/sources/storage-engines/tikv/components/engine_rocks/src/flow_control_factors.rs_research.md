<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/engine_rocks/src/flow_control_factors.rs -->
# sources/storage-engines/tikv/components/engine_rocks/src/flow_control_factors.rs

Purpose: exposes RocksDB flow-control inputs through `engine_traits::FlowControlFactorsExt`.

Important APIs/types/functions: `get_cf_num_files_at_level`, `get_cf_num_immutable_mem_table`, and `get_cf_pending_compaction_bytes` for `RocksEngine`.

Control flow: each method resolves a column-family handle and delegates to utility functions reading RocksDB properties.

State and persistence behavior: read-only runtime inspection of LSM state; no persistent data is modified.

Dependencies/integration: used by flow-control and ingestion logic to reason about write pressure, L0 file count, immutable memtables, and compaction debt.

Risks: values are optional because RocksDB properties can be missing or unsupported; callers must handle `None`. CF lookup errors propagate.

Test signals: import tests use `get_cf_num_files_at_level` to assert preconditions around L0 ingestion placement.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/engine_rocks/src/flow_control_factors.rs -->
