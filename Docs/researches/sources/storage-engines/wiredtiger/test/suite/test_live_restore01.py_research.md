# sources/storage-engines/wiredtiger/test/suite/test_live_restore01.py

## Purpose
Validates live restore connection compatibility rules and configuration error handling.

## APIs, Types, And Functions
Defines `test_live_restore01` extending `backup_base`. Helpers `expect_success`, `expect_failure`, and `expect_failure_rounds` open `DEST` with supplied configs, close or assert `WiredTigerError`, and reset the destination directory. The test uses `take_full_backup` to produce `SOURCE`.

## Control Flow, State, And Persistence
After taking a full backup, the test removes all home files except `SOURCE` and output logs, creates `DEST`, and runs valid and invalid live restore opens. It covers Windows unsupported behavior, in-memory compatibility, empty and missing paths, thread bounds, readonly, salvage, statistics disabled, disaggregated incompatibility, non-live reopen while restore is in progress, and statistics reconfigure rejection.

## Dependencies, Integration, Risks, And Test Signals
Depends on backup infrastructure, filesystem cleanup, live restore config parsing, and exact error-message patterns. Risks include accepting incompatible modes or allowing stats to be disabled during active restore. Signals are successful opens for valid configs and regex-matched errors for invalid configs.
