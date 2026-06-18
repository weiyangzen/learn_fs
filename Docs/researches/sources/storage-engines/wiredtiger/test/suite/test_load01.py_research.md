# sources/storage-engines/wiredtiger/test/suite/test_load01.py

## Purpose
Smoke-tests dynamic `load_control` reconfiguration and validation bounds.

## APIs, Types, And Functions
Defines `test_load01` using `conn_config="cache_size=50MB,statistics=(all)"`. The test calls `Connection.reconfigure` with `load_control=[enable=...,control_threshold=...]`, table cursors, and `assertRaisesException` for invalid configs.

## Control Flow, State, And Persistence
The test creates a table, writes baseline rows, loops over valid disabled/enabled thresholds from 10 through 100, reconfigures the connection, writes more rows, and confirms the connection remains usable by scanning row count. It then tries threshold 0, negative, and too-large values and expects `Invalid argument`. Table state is only a liveness signal for reconfiguration.

## Dependencies, Integration, Risks, And Test Signals
Depends on runtime config parsing and connection reconfiguration. Risks are accepting invalid thresholds or requiring restart for load control changes. Signals are successful post-reconfigure reads/writes and failures for invalid thresholds with stderr ignored afterward.
