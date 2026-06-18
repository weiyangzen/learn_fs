# sources/storage-engines/tikv/tests/failpoints/cases/test_table_properties.rs

See the grouped report section in `Docs/researches/groups/subset-b-008947_research.md` for the full source-aligned research. Summary: this file tests raw-key-mode GC compaction-filter decisions driven by RocksDB table properties. It builds API v2 temp engines, writes encoded raw values, flushes SSTs, runs `TestGcRunner::gc_raw` and `gc_on_files`, and verifies `GC_COMPACTION_FILTER_PERFORM` and `GC_COMPACTION_FILTER_SKIP`. It covers safepoint checks, bottommost-level behavior, and version/row ratio thresholds.
