# sources/storage-engines/wiredtiger/test/suite/test_tiered12.py

## Purpose
`test_tiered12.py` checks that `flush_tier` returns after the shared-storage copy completes and does not wait unnecessarily for delayed `flush_finish` work.

## Important APIs, Types, and Functions
The class uses `TieredConfigMixin`, `get_conn_config`, `get_check`, and `timing_stress_for_test=(tiered_flush_finish)`. Connection config sets short local retention and a one-second artificial delay in flush finish.

## Control Flow
`test_tiered` creates a tiered table, writes one record, verifies it, and calls forced `checkpoint('flush_tier=(enabled,force=true)')`. For directory store it immediately checks that the bucket object exists, then sleeps long enough for delayed background flush-finish processing.

## State and Persistence Behavior
The test distinguishes completion of copying an object to shared storage from later local/cache finish work. The expected state after the flush call is that the shared object already exists even though finish work can lag.

## Dependencies and Integration Points
It integrates with tiered manager timing-stress hooks, directory-store bucket files, checkpoint flush code, and helper readback checks.

## Risks and Test Signals
The risk is synchronous flush waiting on unnecessary finish work or returning before the copy is durable in the bucket. The signal is successful forced flush and immediate directory-store object existence.
