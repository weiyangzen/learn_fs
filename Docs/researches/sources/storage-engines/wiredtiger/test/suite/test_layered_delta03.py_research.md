# sources/storage-engines/wiredtiger/test/suite/test_layered_delta03.py

Purpose: verifies that `page_delta=(max_consecutive_delta=1)` prevents reading a long leaf delta chain by forcing full images often enough that follower reads do not report leaf-delta reads.

Important APIs and functions: `test_layered_delta03` uses URI scenarios for `layered:` and `file:` with `block_manager=disagg`, `stat.conn.cache_read_leaf_delta`, `session.checkpoint`, follower reopen with `checkpoint_meta`, and ordinary cursor indexing for reads and writes.

Control flow: the test loads 1000 rows, checkpoints, updates every tenth row, checkpoints, repeats the same update pattern and checkpoints again, then reopens as a follower. It verifies visible values and asserts `cache_read_leaf_delta` is zero.

State and persistence behavior: repeated checkpoints with a low consecutive-delta limit should materialize a full image instead of requiring follower delta-chain reads. The expected state is latest values for every tenth key and original values for the rest.

Dependencies and integration: integrates page delta policy configuration, disaggregated block manager, follower checkpoint metadata, and connection statistics. Risks include ignoring the consecutive-delta cap, creating a readable but unexpectedly long chain, or stat misclassification of full-image reads. Test signals are exact data verification plus zero leaf-delta read statistic.
