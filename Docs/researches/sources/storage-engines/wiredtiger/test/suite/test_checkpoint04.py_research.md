# sources/storage-engines/wiredtiger/test/suite/test_checkpoint04.py

Purpose: validates checkpoint timing statistics are populated and ordered as expected, especially that preparation timing is less than total checkpoint timing.

Important APIs/types/functions: `SimpleDataSet`, `stat.conn.checkpoints_api`, `checkpoint_state`, `checkpoint_prep_running`, `checkpoint_prep_min/max/recent/total`, `checkpoint_time_min/max/recent/total`, `reopen_conn`, and precise/fuzzy scenarios.

Control flow: in a retry loop with increasing value size, create 50 tables, update 100 rows per table, checkpoint, recreate/update tables with a different value, checkpoint again, read and print timing stats, assert checkpoint count, state, and prep_running values, and exit only when prep stats are all less than corresponding total time stats. Reopen resets stats between retries and fails if multiplier reaches 100.

State/persistence behavior: workload creates enough dirty data across many tables for measurable checkpoint timings. Statistics are the main persisted connection state under test.

Dependencies/integration: statistics subsystem, checkpoint implementation, precise checkpoint stable timestamp requirement, and dataset helper.

Risks/test signals: designed to handle coarse timers by retrying; failures may be platform timing issues or bad stat accounting.
