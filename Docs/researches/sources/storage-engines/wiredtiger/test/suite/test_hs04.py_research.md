# sources/storage-engines/wiredtiger/test/suite/test_hs04.py

## Purpose

Verifies configuration and reconfiguration of history-store `file_max`, including in-memory mode where HS disk settings are ignored.

## Important APIs, Types, and Functions

Defines `WT_MB`, scenario products for initial file max, reconfigured file max, and `in_memory`, plus `conn_config`, `get_stat`, and `test_hs`.

## Control Flow

The connection opens with optional `history_store=(file_max=...)` and optional `in_memory`. The test creates a table, checks `cache_hs_ondisk_max`, reconfigures `history_store.file_max`, expects either a below-minimum error or updated stat, and repeats in-memory expectations.

## State and Persistence Behavior

State is configuration-derived connection statistic state. No history-store workload is generated.

## Dependencies and Integration Points

Depends on `wiredtiger`, `wttest`, scenario generation, connection reconfigure, and `stat.conn.cache_hs_ondisk_max`.

## Risks and Maintenance Signals

It validates stat values, not actual file-size enforcement. Minimum boundary expectations assume 99MB remains below the configured lower bound.

## Test Signals

Signals are exact stat values for default/100MB/0, rejection of too-low reconfigure, and ignored HS settings under in-memory mode.
