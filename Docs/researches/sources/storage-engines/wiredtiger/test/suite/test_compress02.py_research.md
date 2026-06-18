<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_compress02.py -->
# sources/storage-engines/wiredtiger/test/suite/test_compress02.py

Purpose: verifies that zstd compression level can be changed after restart while existing tables remain readable using the original compression settings.

Important APIs and control flow: `conn_config()` starts with `builtin_extension_config={zstd={compression_level=6}}`. The test creates a zstd-compressed table, writes 1000 large values one transaction per key through `large_updates()`, verifies all values in `check()`, checkpoints, copies the WiredTiger home to `RESTART`, closes, and reopens the copy with compression level 9.

State, persistence, and dependencies: persisted table pages and metadata survive a simulated crash/restart via `copy_wiredtiger_home`. Dependencies are zstd extension loading, `SimpleDataSet`, `wttest.zstdtest`, checkpoint durability, and cursor iteration.

Integration points: exercises builtin extension configuration parsing, zstd compressor state, recovery/reopen, and metadata compatibility between old and new compressor levels.

Risks and test signals: only readability is asserted, not that newly written pages use the new level. A pass means data written at level 6 remains readable after reopening with level 9; failure indicates zstd config, metadata persistence, or restart/recovery issues.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_compress02.py -->
