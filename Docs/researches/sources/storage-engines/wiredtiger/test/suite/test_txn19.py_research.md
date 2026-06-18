# sources/storage-engines/wiredtiger/test/suite/test_txn19.py

## Purpose
`test_txn19.py` tests recovery and salvage behavior when transaction log files or core metadata files are corrupted in many ways.

## Important APIs, Types, and Functions
The module-level `corrupt` helper mutates files. `test_txn19` models log corruption with helpers for log-file mapping, expected corruption, recovery failure, recovered record count, and `test_corrupt_log`. `test_txn19_meta` corrupts `WiredTiger`, `WiredTiger.basecfg`, `WiredTiger.turtle`, `WiredTiger.wt`, and `WiredTigerHS.wt` and tests open/salvage expectations.

## Control Flow
Log tests create large records so log files contain predictable record counts, copy a crash home, corrupt selected logs, attempt normal recovery, run salvage, validate recovered records, insert more records, and recover again. Metadata tests create several tables, copy homes, corrupt one metadata file, try normal open, then test salvage paths on two copies.

## State and Persistence Behavior
This file directly mutates persisted log and metadata files and marks the database corrupted. It verifies which damage is fatal, warning-only, openable, salvageable, or recoverable.

## Dependencies and Integration Points
Depends on `helper.copy_wiredtiger_home`, `wiredtiger_open`, salvage config, stdout/stderr pattern expectations, and scenario pruning.

## Risks and Edge Cases
It is highly platform- and message-sensitive. Some combinations are intentionally classified as benign because partial final log records can resemble crash remnants.

## Test Signals
Expected opens fail or succeed with matched errors/warnings, salvage yields expected records where supported, and subsequent recovery preserves inserted records.
