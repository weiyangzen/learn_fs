# sources/storage-engines/foundationdb/contrib/convert.py

## Purpose
Interactive utility for converting between Unix timestamps and FoundationDB versions using the system-key Timekeeper map in a specific cluster.

## Important APIs, Types, And Functions
The script initializes `fdb.api_version(730)` and opens a hard-coded cluster file. `find_version_for_timestamp()` scans `\xff\x02/timeKeeper/map/` for the nearest version at or before/after a timestamp. `find_timestamp_for_version()` does a binary search over Timekeeper keys to estimate a timestamp for a version. CLI subcommands are `getVersion` and `getTime`.

## Control Flow
`getVersion` parses three timestamps and prints corresponding start/end/mutation versions. `getTime` parses one version, calls the binary search helper, and prints Unix and local formatted time. Both transactional helpers enable system-key and lock-aware reads.

## State And Persistence
The script does not mutate the database. It reads FoundationDB system keys in snapshot transactions. The only persistent dependency is the hard-coded cluster file path.

## Dependencies And Integration
Requires the FoundationDB Python binding and access to a live cluster with Timekeeper data. It integrates with internal system key encoding via `fdb.tuple` and `fdb.KeySelector`.

## Risks
The cluster file is environment-specific and prevents general use without editing the file. `strinc()` is referenced but not defined, so the `start=False` branch in `find_version_for_timestamp()` is broken. Binary search uses `ts_cur`/`version_cur` after loops where they may not be assigned if the range is empty. The code assumes timestamps and versions are monotonic enough for interpolation and uses a fixed `1e6` versions/sec estimate outside recorded bounds.

## Test Signals
Mock transactions and Timekeeper ranges for exact match, before-min, after-max, empty map, and nearest-boundary lookups. A real integration test needs a disposable cluster with system key reads enabled.
