# sources/storage-engines/wiredtiger/test/suite/test_layered_checkpoint11.py

Purpose: verifies a follower can pick up multiple checkpoints for the same layered table and read the latest values after each pickup. It includes a `debug_mode=(cursor_copy=true)` variant to catch metadata cursor value lifetime/use-after-free issues under sanitizers.

Important APIs/types/functions: uses `follower_conn_config`, `insert_data`, `check_data`, `disagg_advance_checkpoint`, `gen_disagg_storages`, `make_scenarios`, and optional `debug_mode=(cursor_copy=true)`.

Control flow: leader creates a layered table, writes `v1-` values, and checkpoints. A follower opens and picks up checkpoint 1, then verifies all rows. The leader writes `v2-` values and checkpoints; follower advances and verifies replacement values. A third `v3-` round repeats the same path to ensure repeated updates remain correct.

State and persistence behavior: table content is overwritten in-place across checkpoints. Follower local metadata is first inserted, then updated on later checkpoint pickups. The cursor-copy scenario stresses that metadata strings used during pickup are not referenced after their cursor buffers become invalid.

Dependencies/integration points: follower checkpoint pickup, local metadata insertion/update, shared metadata parsing, and debug cursor-copy mode.

Risks: fixed 100-row coverage is functional but not broad for page layout; the test targets metadata correctness more than storage scaling.

Test signals: pass means repeated follower pickup for one table returns latest data and remains valid when cursor values are copied/freed differently.
