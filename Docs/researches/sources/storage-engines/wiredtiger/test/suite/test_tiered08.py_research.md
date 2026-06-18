# sources/storage-engines/wiredtiger/test/suite/test_tiered08.py

## Purpose
`test_tiered08.py` stress-tests concurrent inserts with background checkpoints and occasional tier flushes.

## Important APIs, Types, and Functions
The class uses `TieredConfigMixin`, `flush_checkpoint_thread`, fast statistics, and `timing_stress_for_test=(tiered_flush_finish)`. Helpers `get_stat`, `key_gen`, `value_gen`, `populate`, and `verify` control workload generation and validation.

## Control Flow
`test_tiered08` creates a tiered table with small pages, starts a background `flush_checkpoint_thread` that checkpoints every millisecond and flushes roughly one quarter of the time, then inserts batches of 100,000 keys until the connection statistics reach at least 200 checkpoints and 50 flushes. During population it periodically opens a reader cursor to touch existing data. After stopping the thread, it verifies sampled keys, closes and reopens the connection, and verifies again.

## State and Persistence Behavior
The workload creates a large table while checkpoint and tiered object switching can interleave with active writes. Restart verification tests that local and shared tier state remain consistent after concurrent operations.

## Dependencies and Integration Points
It integrates with `wtthread.flush_checkpoint_thread`, connection statistics `checkpoints_api` and `flush_tier`, tiered flush timing stress, and normal cursor read/write paths.

## Risks and Test Signals
Risks include races among checkpoint, flush-finish, object switching, and active writes. Signals are reaching the target stats without errors and sampled key/value correctness before and after reopen.
