# sources/storage-engines/wiredtiger/test/cppsuite/src/component/timestamp_manager.cpp

Purpose: Manages test timestamps and advances WiredTiger stable/oldest timestamps within configured lag windows.

Important APIs/types/functions: `decimal_to_hex` and `hex_to_decimal` convert timestamp formats. `load` reads oldest/stable lag seconds and shifts them into the high 32 timestamp bits. `do_work` computes current logical time, advances stable and oldest when lag windows expire, calls `connection_manager::set_timestamp`, and updates local atomics after WT is updated. `get_next_ts` combines steady-clock seconds with an atomic increment. `get_valid_read_ts` returns a random timestamp between oldest and just before stable.

Control flow: the component run loop periodically calls `do_work`. Timestamp publication order is intentional: set WT timestamps first, then update local oldest/stable values used by sweep/read helpers.

State and persistence: maintains `_increment_ts`, `_oldest_ts`, `_stable_ts`, and lag windows in memory; persists timestamp state into the WiredTiger connection.

Dependencies/integration: depends on `connection_manager`, `configuration`, random generator, logger, and WT timestamp types. Operation tracking uses `get_oldest_ts`; database/workload operations use `get_next_ts`.

Risks and test signals: steady-clock timestamps are process-relative, not wall-clock. `get_valid_read_ts` can race with oldest advancement but relies on timestamp rounding. Assertions catch oldest/stable inversion and hex parse failures.
