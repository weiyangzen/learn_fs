# sources/storage-engines/wiredtiger/test/suite/test_layered_checkpoint15.py

Purpose: validates checkpoint timestamp publication and follower visibility across layered-prefix, table-with-layered-type, and shared disaggregated table configurations.

Important APIs/types/functions: uses `disagg_get_complete_checkpoint_ext`, `disagg_advance_checkpoint`, `query_timestamp('get=last_checkpoint')`, timestamped transactions, and scenarios for `layered:`, `table:` with `block_manager=disagg,type=layered`, and shared `block_manager=disagg,log=(enabled=false)`.

Control flow: phase 1 writes all rows at timestamp 100, sets stable 100, checkpoints, verifies checkpoint timestamp, opens follower, advances, checks follower last checkpoint timestamp and all values. Phase 2 updates every 50th row at timestamp 200, checkpoints at stable 200, advances follower, and verifies mixed old/new values. Phase 3 updates every 25th row at timestamp 300 but checkpoints at stable 250, advances follower, and verifies timestamp-300 changes are not visible. It then advances leader stable timestamp to include all data for clean teardown.

State and persistence behavior: stable timestamp, commit timestamp, checkpoint timestamp, and follower-visible values are the key state. The third phase confirms checkpoint content follows stable timestamp rather than latest committed timestamp.

Dependencies/integration points: timestamp visibility, disaggregated checkpoint metadata, follower pickup, multiple table configuration styles.

Risks: high row count across scenario matrix increases runtime. The test assumes timestamped visibility semantics are identical across layered and shared modes.

Test signals: pass proves checkpoint timestamps match stable timestamps and followers see only data stable at the checkpoint.
