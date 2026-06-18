# sources/storage-engines/wiredtiger/test/suite/test_util01.py

## Purpose
`test_util01.py` tests `wt dump` and dump cursors for byte-array key/value data, printable and hex output, and timestamp-filtered process dumps.

## Important APIs, Types, and Functions
The class defines byte generation/formatting helpers (`get_bytes`, `dumpstr`, `dump_kv_to_line`), comparison helpers, `write_entries`, `dump`, and seven test methods. It uses `wiredtiger.wiredtiger_version`, `runWt(['dump'])`, dump cursors, and timestamped commits.

## Control Flow
Each test creates a `key_format=u,value_format=u` table, writes deterministic binary-like keys and values, builds `expect.out` in the expected dump format, produces `dump.out` via either the `wt` process or dump cursor, and compares the files. Timestamp cases write at two timestamps and dump at a read timestamp.

## State and Persistence Behavior
The table stores all byte values including null terminators. Timestamped cases verify dump reads only versions visible at the requested timestamp.

## Dependencies and Integration Points
Depends on the external `wt dump` utility, dump cursor API, filesystem output files, and binary formatting conventions.

## Risks and Edge Cases
Output is deliberately format-sensitive. The comparison relaxes header config ordering but not data formatting.

## Test Signals
`expect.out` and `dump.out` compare equal for process/API, print/hex, and timestamp cases.
