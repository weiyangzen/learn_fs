# sources/sync-backup/borg/src/borg/testsuite/crypto/file_integrity_test.py

Purpose: tests Borg's file integrity wrappers for detached `.integrity` files, inline integrity data, part-level hashing, `SyncFile` integration, and SHA-256 hashing behavior.

Important APIs and control flow: `TestReadIntegrityFile` covers missing, truncated, unknown-algorithm, and malformed integrity metadata. `TestDetachedIntegrityCheckedFile` writes protected data, verifies normal reads, detects appended corruption, detects corruption even after partial reads, treats rename as path-bound integrity failure, permits moving a file and sidecar together, and tolerates missing integrity files. `TestDetachedIntegrityCheckedFileParts` validates named part hashes, wrong part names, and independence of verified leading parts from later appended corruption while still failing final digest. `TestIntegrityCheckedFileWithSyncFile` wraps a `SyncFile` override and reuses captured `integrity_data`. `TestSHA256FileHashingWrapper` checks pure and impure hash modes, including file-length suffixing in impure mode.

State and persistence: uses pytest temporary directories to create real files and sidecar `.integrity` JSON files. Integrity depends on file contents, file name/path binding, named parts, and final digest state.

Dependencies and integration points: depends on `DetachedIntegrityCheckedFile`, `IntegrityCheckedFile`, `SHA256FileHashingWrapper`, `FileIntegrityError`, and platform `SyncFile`. This protects repository index/hints/integrity sidecars and other metadata files.

Risks: the API deliberately fails closed after a part hash mismatch, so broad exception handling around `hash_part` still leads to final failure. Rename sensitivity is useful for tamper detection but can surprise callers that rename protected files without regenerating metadata.

Test signals: successful readback, expected `FileIntegrityError` on malformed or corrupted data, path/move behavior, part isolation, and known SHA-256 digests.
