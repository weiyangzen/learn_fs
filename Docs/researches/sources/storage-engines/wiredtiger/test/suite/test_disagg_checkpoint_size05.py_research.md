# sources/storage-engines/wiredtiger/test/suite/test_disagg_checkpoint_size05.py

Purpose: ensures `stat.dsrc.block_size` reflects disaggregated checkpoint size for stable files and agrees across slow and fast statistics paths.

Important APIs and control flow: helpers insert rows, read `block_size` from `statistics:<stable_uri>` with `statistics=(all)` and `statistics=(size)`, and parse metadata `size=` as ground truth. Tests cover zero before first checkpoint, agreement with metadata, growth after new checkpoint, correctness after restart, layered URI aggregation, unchanged value without checkpoint even after eviction, and crash survival.

State and persistence: the statistic must reflect the last successful checkpoint, not dirty uncheckpointed data. Restart initializes block manager handles from metadata.

Dependencies and integration: uses `@disagg_test_class`, `wiredtiger.stat`, `simulate_crash_restart`, layered and stable URIs, metadata cursors, and debug eviction.

Risks and test signals: mismatches indicate fast-path metadata reads, slow-path dhandle initialization, or checkpoint/crash accounting regressions.
