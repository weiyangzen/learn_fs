# sources/storage-engines/wiredtiger/test/suite/test_layered_delta12.py

Purpose: broader internal page delta correctness coverage for disaggregated file tables. It covers internal updates, inserting keys at the end of a base image, base images that have extra tail keys during merge, and keys updated multiple times.

Important APIs and functions: `test_layered_delta12` uses page-delta scenarios for leaf-only, internal-only, both, and none; large cache, small page sizes, `stat.conn.rec_page_delta_internal`, `rec_page_delta_leaf`, `cache_read_internal_delta`, helpers `insert`, `verify`, and `get_stat`.

Control flow: each test creates a dense table, checkpoints a base image, applies a pattern of timestamped key/value changes, checkpoints, checks write statistics according to delta configuration, reopens, and verifies merged values. Some tests compare internal delta read counts before and after reopen to ensure internal deltas were actually consumed.

State and persistence behavior: these tests exercise merge boundaries where modified keys are at the end of the base image, where base images contain more keys than the delta side, and where one key has multiple updates. The expected persisted state is a merge of unchanged initial values plus targeted modifications.

Dependencies and integration: integrates internal/leaf delta configuration, page-log apply, connection statistics, timestamped writes, and full-table verification. Risks include key-order merge bugs, tail-key loss, repeated-update collapse errors, and misreporting delta type. Test signals are statistic assertions and exhaustive key/value verification.
