# sources/storage-engines/wiredtiger/test/suite/test_prepare28.py

## Purpose

Regression test for reading a partial prepared transaction with `ignore_prepare=true` during prepare resolution.

## Important APIs, Control Flow, and State

The test is skipped for tiered storage and enables `timing_stress_for_test=[prepare_resolution_2]`, which sleeps during prepare resolution. One session prepares three updates to key 1 at timestamp 4. A second thread waits briefly, opens a transaction with `ignore_prepare=true`, hits `session.breakpoint()`, and searches key 1 while the main thread commits at timestamp 6. The expected search return is `-31803`, and connection statistic `txn_read_race_prepare_commit` must be greater than zero.

## Dependencies, Risks, and Test Signals

Dependencies are `wtthread.Thread`, timing stress, WiredTiger statistics, and thread interleaving. The risk is exposing a subset of updates from one prepared transaction while resolution is in progress. Signals are the special return code and race statistic increment.
