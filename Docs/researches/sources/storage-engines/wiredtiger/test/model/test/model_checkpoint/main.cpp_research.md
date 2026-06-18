# sources/storage-engines/wiredtiger/test/model/test/model_checkpoint/main.cpp

## Purpose
This executable validates the model's checkpoint semantics against WiredTiger. It covers stable-timestamp checkpoint visibility, named and unnamed checkpoints, prepared transaction checkpoint rules, restart-time checkpoint discovery, and logged table differences where stable timestamps do not filter logged updates the same way.

## Important APIs, Types, and Functions
The central types are `model::kv_database`, `model::kv_table_ptr`, `model::kv_checkpoint_ptr`, and `model::kv_transaction_ptr`. Model-only coverage is in `test_checkpoint` and `test_checkpoint_logged`; WiredTiger comparison paths are `test_checkpoint_wt`, `test_checkpoint_restart_wt`, and `test_checkpoint_logged_wt`. The test uses model checkpoint calls (`create_checkpoint`, `checkpoint`, `set_stable_timestamp`, `restart`) and WT helpers (`wt_model_ckpt_create_both`, `wt_model_ckpt_assert`, `wt_model_txn_begin_both`, `wt_model_txn_prepare_both`, `wt_model_txn_commit_both`, `wt_print_debug_log`).

## Control Flow
Each scenario builds a sequence of transactional inserts, advances stable timestamps, creates checkpoints, and asserts checkpoint reads for selected keys. The WT scenarios open multiple sessions to model concurrent transactions, create tables with `log=(enabled=false)` or `log=(enabled=true)`, then verify current table state and checkpoint state. Some scenarios close and reopen the database specifically so the debug log can be printed and replayed into a fresh `kv_database`.

## State, Persistence, and Integration
The file tests checkpoint state as a durable snapshot boundary: committed data before the stable timestamp should be visible, uncommitted or too-new data should be absent, and prepared transactions depend on prepare/commit/durable timestamps. `test_checkpoint_restart_wt` chains named checkpoints across multiple reopen cycles and prepared transactions to ensure retained debug-log metadata can reconstruct checkpoints after restart. Logged table scenarios intentionally ignore stable timestamps for logged data and validate that behavior in both model and WT paths.

## Risks and Test Signals
Checkpoint semantics are highly coupled to timestamp rules, prepared transaction durability, debug logging, and checkpoint retention. Risk areas include moving the stable timestamp backwards, committing prepared transactions with durable timestamps after stable, leaving prepared work in checkpoints, and interpreting logged table checkpoints. Test signals include `contains_any` checks for multiple values at one key, `verify_noexcept` against named checkpoints, debug-log and JSON replay parity, and model exceptions for illegal timestamp ordering.
