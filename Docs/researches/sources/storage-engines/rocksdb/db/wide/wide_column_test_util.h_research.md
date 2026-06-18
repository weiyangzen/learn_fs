# sources/storage-engines/rocksdb/db/wide/wide_column_test_util.h

Purpose: This header provides small inline helpers shared by wide-column and blob integration tests. It centralizes generation of predictable inline/blob-sized values and option presets for blob-file and blob-direct-write scenarios.

Important APIs/types/functions: `GenerateLargeValue(size, fill_char)` returns a repeated-character string intended to exceed blob thresholds. `GenerateSmallValue()` returns `"small"`. `GetOptionsForBlobTest(default_options)` copies caller defaults, enables blob files, sets `min_blob_size = 10`, creates DBs if missing, and disables automatic compactions. `GetBlobDirectWriteCompatibleOptions(default_options)` disables concurrent memtable writes. `GetDirectWriteOptions(default_options)` enables blob files, blob direct write, sets `min_blob_size = 32`, and uses one direct-write partition.

Control flow: All helpers are inline and side-effect-free except for mutating a local `Options` copy. The blob-test path preserves fixture-specific defaults such as custom environments, then layers blob settings. The direct-write path first applies compatibility constraints before enabling direct-write-specific knobs.

State and persistence behavior: These helpers influence where test values persist: small values generally remain inline in LSM data, while values above `min_blob_size` become blob-backed when blob files/direct write are enabled. Disabling auto compaction makes flush/compaction timing deterministic for tests.

Dependencies and integration points: The file depends only on `<string>` and `rocksdb/options.h`, and lives under `wide_column_test_util` in `ROCKSDB_NAMESPACE`. It integrates with DB test fixtures that need blob extraction or direct write without duplicating option setup.

Risks: The "large" and "small" classifications are threshold-dependent; callers changing `min_blob_size` can invalidate assumptions. Direct write requires `allow_concurrent_memtable_write = false`, so tests using these options do not cover the concurrent memtable path.

Test signals: This is a utility header without its own tests, but its consumers validate blob-backed wide-column behavior. Its deterministic defaults are themselves a test signal: small thresholds force blob extraction with compact fixture data.
