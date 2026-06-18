# sources/storage-engines/tikv/src/import/duplicate_detect.rs

## Purpose
Scans MVCC write records to detect duplicate keys during Lightning/import workflows, returning duplicate key/value/commit-ts batches through `DuplicateDetectResponse`.

## Important APIs, Types, and Functions
`DuplicateDetector<S: Snapshot>` owns a snapshot, write-CF iterator, `key_only` flag, validity flag, and `min_commit_ts`. `new` builds encoded lower/upper bounds over `CF_WRITE` and seeks to the start key. `try_next` returns batches capped by `MAX_SCAN_BATCH_COUNT`. `move_to_next_import_key`, `collect_current_key_duplicate`, `skip_lock_and_rollback`, `skip_all_version`, and `make_kv_pair` implement MVCC traversal. It implements `Iterator<Item = DuplicateDetectResponse>`.

## Control Flow
The detector scans write CF entries ordered by encoded user key and commit timestamp. It only starts duplicate collection when it sees a commit ts greater than `min_commit_ts`. For a key, the first put above the threshold is remembered, subsequent put versions are emitted as duplicate pairs, and traversal stops for that key once an older non-import version or delete is encountered. Rollback and lock records are skipped. If value materialization is requested and the write has no short value, the default CF value is loaded by start_ts.

## State and Persistence Behavior
The detector is read-only over a snapshot. It advances a single iterator and marks itself invalid after the first error so streaming stops cleanly. Responses carry either pairs or a key error.

## Dependencies and Integration Points
Uses engine traits `CF_WRITE`, `CF_DEFAULT`, MVCC `Key`, `TimeStamp`, `WriteRef`, `WriteType`, TiKV snapshots, and importer protobufs. `ImportSstService::duplicate_detect` wraps it in a server-streaming RPC after obtaining an async snapshot.

## Risks and Edge Cases
It treats unexpected delete/rollback/lock as errors when the first import-version record above `min_commit_ts` is not a put. Missing default-CF value for a long value is a hard RocksDB error. Error conversion includes a typo in "unkown" and maps many kv errors to a generic RocksDB message. Correctness depends on MVCC key ordering and commit-ts semantics.

## Test Signals
Tests cover base duplicate detection, incremental `min_commit_ts` behavior, rollback/delete handling, long values, and expected ordering. They use transactional test storage and compare emitted batches. Key-only mode and iterator `next` error responses are less directly covered.
