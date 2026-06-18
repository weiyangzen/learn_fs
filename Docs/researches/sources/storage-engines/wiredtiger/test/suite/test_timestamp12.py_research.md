# sources/storage-engines/wiredtiger/test/suite/test_timestamp12.py

## Purpose
`test_timestamp12.py` tests the `use_timestamp` setting when closing a connection, contrasting checkpoint-durable and log-durable tables.

## Important APIs, Types, and Functions
The class uses `conn_config='config_base=false,create,log=(enabled)'`, scenarios for key format and close configuration, `verify_expected`, `close_conn(close_cfg)`, and `open_conn`.

## Control Flow
The test creates a logged table and a non-logged checkpoint table, inserts a first range of keys with commit timestamps and advances oldest/stable to the end of that range, then inserts a second range without advancing stable. It closes and reopens using default close config, `use_timestamp=true`, or `use_timestamp=false`. Expected results are built so logged data always includes all keys, while the non-logged table includes only stable-range keys unless `use_timestamp=false` requests all dirty data.

## State and Persistence Behavior
Close-time checkpoint policy determines whether unstable non-logged updates are persisted. Logged data is independent of stable close behavior because it is recovered from the log.

## Dependencies and Integration Points
It integrates with close-time checkpoint configuration, recovery, logging, non-logged checkpoint durability, and cursor iteration.

## Risks and Test Signals
Risks include changing the default stable-close policy or applying it to logged tables incorrectly. Signals are exact recovered dictionaries for logged and checkpoint tables.
