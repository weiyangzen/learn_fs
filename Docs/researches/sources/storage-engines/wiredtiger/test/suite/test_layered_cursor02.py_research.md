# sources/storage-engines/wiredtiger/test/suite/test_layered_cursor02.py

Purpose: verifies `cursor.modify` remains valid on a follower after reopening from a checkpoint, for both item (`u`) and string (`S`) value formats.

Important APIs/types/functions: uses `DisaggConfigMixin`, PALite page log config, `modify_utils.create_value`, `modify_utils.create_mods`, deterministic `random.Random(42)`, `cursor.modify`, timestamped commits, and `reopen_conn` with `checkpoint_meta`.

Control flow: leader creates a layered table with selected value format, inserts 1,000 random large values, stores originals, and checkpoints. It reopens the same home as follower with the latest checkpoint metadata. For each key, it computes modifications from the original value, applies `cursor.modify` in a timestamped transaction, commits, and asserts reading the key returns the expected new value.

State and persistence behavior: base values are checkpointed; modifies are applied after checkpoint pickup on follower state. The test verifies modify can reconstruct from the checkpointed base value and produce correct current values.

Dependencies/integration points: disaggregated checkpoint pickup, modify vector application, item/string value formats, PALite page log, and modify utility generation.

Risks: variables `size`, `repeats`, `nmods`, and `maxdiff` used during modification are the last generated values from the insert loop, not per-key values; `create_mods` still uses each key's old value, but the distribution is less varied than it appears.

Test signals: pass means follower-side modify after checkpoint pickup works for both raw item and string formats.
