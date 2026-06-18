# sources/storage-engines/wiredtiger/test/suite/test_cc08.py

Purpose: verifies checkpoint cleanup selects logged tables for cleanup only when configured in aggressive reclaim-space mode.

Important APIs/types/functions: inherits `test_cc_base`, uses `make_scenarios`, config `checkpoint_cleanup=[method=none|reclaim_space]`, connection stats `checkpoint_cleanup_pages_read_reclaim_space` and `checkpoint_cleanup_pages_visited`, and skips tiered storage.

Control flow: create a logged small-page table, populate 1,000 rows, checkpoint, reopen with the scenario cleanup method, open a cursor to ensure the data handle is active, force cleanup, then assert selected/visited page stats are positive for `reclaim_space` and zero selected pages for `method=none`.

State/persistence behavior: table is logged and clean on disk after restart. Reclaim-space cleanup should read pages for possible cleanup only under aggressive mode.

Dependencies/integration: logged table handling, checkpoint cleanup method config, dhandle activation, stats.

Risks/test signals: failure means method gating is wrong or logged-table cleanup selection did not run.
