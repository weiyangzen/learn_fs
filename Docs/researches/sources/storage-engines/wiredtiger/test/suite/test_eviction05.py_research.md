# sources/storage-engines/wiredtiger/test/suite/test_eviction05.py

## Purpose

Validates eviction maximum page-size statistics for clean, dirty, and update pages, and verifies per-checkpoint maximum stats reset at checkpoint.

## Important APIs, Types, and Functions

Defines `test_eviction05`, `conn_config`, `get_stat`, and `test_eviction_page_size_stats`; uses connection stats for maximum clean, dirty, and updates page size per checkpoint.

## Control Flow

The test creates and commits a row, evicts it while dirty/update state is present, checks dirty/update max stats increased and clean did not, reads the clean page back, evicts it again, checks clean stat increased, then checkpoints and expects all per-checkpoint max stats to reset to zero.

## State and Persistence Behavior

State is connection-level statistic accounting across eviction events and a checkpoint boundary. User data is minimal.

## Dependencies and Integration Points

Depends on `wiredtiger.stat`, `wttest`, debug `release_evict`, and statistics logging. Skipped for disaggregated mode.

## Risks and Maintenance Signals

The opening comment says database-run stats are not reset, but the assertions check per-checkpoint stats reset to zero; documentation drift may confuse maintainers.

## Test Signals

Signals are expected nonzero/zero page-size stat transitions and reset after checkpoint.
