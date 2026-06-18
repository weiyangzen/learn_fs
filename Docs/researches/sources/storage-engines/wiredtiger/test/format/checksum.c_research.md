# sources/storage-engines/wiredtiger/test/format/checksum.c

## Purpose
`checksum.c` computes a deterministic FNV-1a hash across all known row-store tables at the stable timestamp. It is used by disaggregated multi-node validation to compare leader and follower database contents.

## Important APIs, Types, And Functions
The exported function is `uint64_t checksum_database(WT_SESSION *)`. Static helpers are `checksum_key`, `checksum_value`, and `checksum_table`, with `struct checksum_table_arg` carrying the session and rolling hash. It uses `tables_apply`, `atou32`, `wt_wrap_begin_transaction`, `session->timestamp_transaction_uint`, `wt_wrap_open_cursor`, and cursor iteration.

## Control Flow
`checksum_database` initializes the FNV hash and applies `checksum_table` to every table. Each table checksum asserts row-store type, begins a read transaction, pins the read timestamp to `g.stable_timestamp`, opens a cursor, walks records in key order, hashes the numeric key portion after any configured prefix, hashes the value bytes, closes the cursor, and rolls back the read transaction.

## State And Persistence Behavior
The function is read-only. It opens timestamped read transactions but never commits, writes, or persists files. Its output hash is stored by callers, notably the shared-memory `DISAGG_MULTI_DB_HASH` in multi-node disaggregated tests.

## Dependencies And Integration Points
It depends on row-store key encoding, `BTREE_PREFIX_LEN`, stable timestamp maintenance, and the table list. It integrates directly with `format_disagg.c` for leader/follower validation.

## Risks And Test Signals
Risks include applying it to column-store tables, hashing at a stale or unset stable timestamp, and key parsing assumptions if key format changes. The primary test signal is a matching leader/follower hash; mismatches cause disaggregated validation failure and optional preservation of layered tables.
