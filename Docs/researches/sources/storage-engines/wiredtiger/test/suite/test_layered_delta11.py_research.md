# sources/storage-engines/wiredtiger/test/suite/test_layered_delta11.py

Purpose: verifies that internal page deltas are not built when modifications affect the first key or otherwise change separator-key assumptions in ways unsafe for delta encoding.

Important APIs and functions: `test_layered_delta11` uses `DisaggConfigMixin`, `disaggregated=(page_log=palite)`, `page_delta=(delta_pct=100)`, `stat.dsrc.rec_page_delta_internal`, randomized/string data generation, checkpointing, and standard cursor insert/remove/update operations.

Control flow: `test_single_update` modifies the first key after an initial checkpoint. `test_inserts_to_split` inserts keys that force tree shape changes around the first key and split behavior. `test_deletes` removes keys and checkpoints. Each test reads data-source stats and asserts no internal page delta is created.

State and persistence behavior: internal page deltas depend on stable separator-key mapping. Changes to first keys, splits, and deletes can invalidate a compact internal-delta representation; these scenarios should fall back to safer full-page behavior.

Dependencies and integration: depends on palite page log, disaggregated page delta logic, internal tree reconciliation, and statistics. Risks include unsafe internal delta generation that loses separator keys or corrupts navigation after reload. Test signals are exact zero `rec_page_delta_internal` assertions after targeted mutations.
