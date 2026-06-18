# sources/user-network-fs/rclone/backend/hasher/kv.go

## Purpose
This file implements the hasher backend's kv database record format and database operations for prune, purge, move, get, put, and dump.

## Important APIs, Types, And Control Flow
`hashRecord` stores a fingerprint string, `operations.HashSums`, and creation time. `encode` and `decode` serialize records using gob. `kvPrune` deletes one key. `kvPurge` scans and deletes all keys below a directory prefix. `kvMove` moves either one file record or all records below a directory prefix; `moveHash` performs the delete and put. `kvGet` loads a record, validates fingerprint compatibility including `anyFingerprint`, validates age, and returns one hash value. `kvPut` loads an existing record, discards it if decoding fails, fingerprint differs, or age expired, then merges new hashes and stores the encoded record. `kvDump` emits either full DB output or root-scoped output and records counts for tests. `dumpLine` formats status, kept hash values, record age, and path.

## State And Persistence
The persistent state is a gob-encoded kv bucket keyed by wrapped remote paths. Records include their creation timestamp for expiry and a fingerprint to detect object changes. Directory purge and move operations rely on lexicographic prefix scans. Sticky imported records use `anyFingerprint` and are reported with `stk` status in dumps.

## Dependencies And Integration Points
It depends on rclone `kv`, `fs`, `hash`, and `operations.HashSums`. `commands.go` uses `kvDump`; `hasher.go` uses prune, purge, and move operations; object-level hash code in adjacent files uses `kvGet` and `kvPut`.

## Risks And Test Signals
Risks include gob incompatibility if `hashRecord` changes, prefix scans over path strings with ambiguous slashes, move overwriting existing destination records, `moveHash` deleting source before a failed destination put, age-based invalidation relying on local clock, and full dump holding DB access long enough to affect concurrent operations. Tests should cover decode failures, fingerprint mismatch, timeout, sticky records, directory purge/move prefixes, dump statuses, and put merging multiple hash types.
