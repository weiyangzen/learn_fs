# sources/storage-engines/wiredtiger/test/suite/test_layered_config03.py

Purpose: ensures disaggregated/layered reconciliation does not generate overflow keys or values even with large logical keys/values and small `leaf_key_max`/`leaf_value_max` settings.

Important APIs/types/functions: uses `stat.conn.rec_overflow_key_leaf`, `stat.conn.rec_overflow_value`, random string generation, timestamped per-key transactions, checkpointing, and scenarios for `layered:` and shared `table:` with `block_manager=disagg,log=(enabled=false)`.

Control flow: the test creates a table with `leaf_key_max=256,leaf_value_max=256`, inserts 500 large keys with small values at timestamp 100, and asserts overflow stats remain zero before checkpoint. It checkpoints at stable 100, then performs several large-value updates at timestamp 200, checkpoints at stable 200, and asserts both overflow stats remain zero again.

State and persistence behavior: the state under test is reconciliation output and checkpointed page encoding for disaggregated storage. Large application values should not use standard overflow item machinery in layered storage.

Dependencies/integration points: reconciliation, page encoding, disaggregated block manager, statistics, timestamped checkpointing.

Risks: random strings are not seeded, so exact key/value contents vary; however only overflow counters are asserted. It does not verify row values after restart.

Test signals: pass means both initial large-key writes and later large-value updates avoid overflow key/value generation in the tested configurations.
