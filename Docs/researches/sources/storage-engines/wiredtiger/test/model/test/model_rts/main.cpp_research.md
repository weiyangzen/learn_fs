# sources/storage-engines/wiredtiger/test/model/test/model_rts/main.cpp

## Purpose
This executable validates rollback-to-stable, restart, and crash behavior in the model and in WiredTiger. It checks how stable timestamps bound durable state, how active/prepared transactions are handled by restarts and crashes, and how logged tables differ from non-logged timestamped tables.

## Important APIs, Types, and Functions
The file uses `model::kv_database`, `model::kv_table_ptr`, `model::kv_transaction_ptr`, `model::data_value`, subprocess helpers from `model/test/subprocess.h`, and WT/model bridge helpers from `wiredtiger_util.h`. Scenario functions include `test_rts`, `test_rts_wt`, `test_rts_crash_wt`, `test_restart_wt1`, `test_restart_wt2`, `test_restart_wt3`, `test_crash_wt1`, `test_crash_wt2`, `test_crash_wt3`, and `test_logged_wt`.

## Control Flow
`main` initializes a temporary home and runs all RTS scenarios. Model-only portions directly set stable timestamps, call `rollback_to_stable`, `restart`, or `crash`, and assert visible values. WT portions often execute setup in `in_subprocess` or `in_subprocess_abort` blocks to simulate clean shutdown or crash, then reopen the database in the parent and compare with model state using `wt_model_assert`. After each WT scenario, the debug log is replayed as an additional check.

## State, Persistence, and Integration
The scenarios distinguish rollback before any stable timestamp, rollback after setting stable, restart with and without explicit checkpoints, crash with no checkpoint, crash after checkpoint, and crash with active/prepared transactions. They also test that updates at timestamps lower than newly recovered stable state can still be applied after RTS/restart. Logged table coverage confirms that committed logged updates are not removed by RTS based on stable timestamp, while uncommitted transactions are still lost.

## Risks and Test Signals
Risk centers on crash/restart boundary conditions, especially when checkpoints, stable timestamps, active transactions, and prepared transactions overlap. The subprocess abort paths are important because normal process teardown would not exercise recovery. Strong test signals include stable timestamp equality after reopen, absence or presence of keys around stable boundaries, successful lower-timestamp writes after recovery, and debug-log verification after each scenario. Failures can indicate recovery semantic drift or model/WT mismatch in rollback visibility.
