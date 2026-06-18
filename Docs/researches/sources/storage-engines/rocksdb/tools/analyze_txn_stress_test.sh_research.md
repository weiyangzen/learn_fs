# sources/storage-engines/rocksdb/tools/analyze_txn_stress_test.sh

## Purpose

This debugging script analyzes RocksDB transaction stress-test LOG output around a failed `RandomTransactionVerify` snapshot. It reconstructs committed transactions and expected key values between two snapshots.

## Important APIs, Types, and Functions

It uses environment variables `LOG`, `vn`, `vn_1`, and optional `SET`. It writes intermediate files `/tmp/txn.txt`, `/tmp/names.txt`, `/tmp/changes.txt`, `/tmp/va.txt`, `/tmp/vb.txt`, `/tmp/keys.txt`, and `/tmp/adds.txt`. The implementation is shell pipelines around `grep`, `awk`, `cut`, `sort`, `uniq`, and arithmetic expansion.

## Control Flow

The script prints inputs, extracts transactions committed between snapshots, maps transaction IDs to names, gathers all change lines, computes total inserts, compares read values between prior and failing snapshots, checks missing keys, and validates that per-key inserted deltas reconcile from first to last change.

## State and Persistence Behavior

It reads only the specified LOG but overwrites fixed `/tmp` scratch files. It returns `1` from the sourced shell context on detected inconsistency in the final loop.

## Dependencies and Integration Points

It is meant to be sourced after running a specific `transaction_test` gtest with detailed logging enabled.

## Risks and Test Signals

Risks include fixed temp filenames, brittle field positions, unquoted variables, sourcing assumptions, and log-format dependence. Test signals are manually inspected mismatched keys, missing-key lines, and `inconsistent txn` output.
