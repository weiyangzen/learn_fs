# sources/storage-engines/foundationdb/contrib/metadata_audit/backup_metadata.py

## Purpose
`backup_metadata.py` backs up selected FoundationDB system metadata ranges (`serverList`, `keyServers`, and `serverKeys`) to JSON files and verifies that the backup is readable and matches live data at sampled keys.

## Important APIs, Types, And Functions
The script imports metadata prefixes and range ends plus `set_read_transaction_options` from `fdb_metadata_utils`. `backup_range(db, prefix, end, name, batch_size=10000)` reads a metadata range in batches and returns `{'key': hex, 'value': hex}` entries. `main()` parses `--cluster-file` and `--output-dir`, connects to FDB, backs up three ranges, writes JSON files and `backup_manifest.json`, then verifies JSON structure and live spot checks. Nested transactional `verify_entry` reads system keys with lock-aware and timeout options.

## Control Flow
`main` creates a timestamped output directory, opens the requested or default FDB cluster, calls `backup_range` for each metadata range, writes each result list to JSON, writes a manifest with timestamp/counts/files, then verifies. `backup_range` repeatedly opens read transactions, sets read options, scans from `start` to `end` with a limit, appends hex-encoded entries, and advances `start` to the last key plus `\x00` until a short batch or no batch is returned.

## State And Persistence Behavior
The script persists a backup directory named `<output-dir>_<timestamp>` containing `serverList.json`, `keyServers.json`, `serverKeys.json`, and `backup_manifest.json`. It reads live FoundationDB system keys but does not write to the database. Verification reopens the written JSON and spot-checks sampled entries against current live values.

## Dependencies And Integration Points
It depends on Python `fdb` bindings, `fdb_metadata_utils`, JSON/filesystem modules, and FoundationDB system-key read options. It is intended to pair with a restore script mentioned in usage and final output.

## Risks And Edge Cases
The backup is not guaranteed to be a single consistent snapshot across all batches and all three ranges unless transaction/version behavior in `set_read_transaction_options` enforces that elsewhere. Advancing with `last_key + b'\x00'` is a common exclusive-start trick but should be checked for arbitrary system key encodings. Verification spot-checks only first/middle/last-style samples and can fail if metadata changes between backup and verification. Output directories are timestamped by local time and can collide within a second if reused.

## Test Signals
Tests should mock FDB transactions and metadata utilities to verify batched range scanning, hex encoding, output file/manifest structure, malformed JSON detection, entry structure validation, spot-check success/failure, empty ranges, and non-default cluster-file handling. Integration tests require a controlled FDB cluster and stable metadata during backup.
