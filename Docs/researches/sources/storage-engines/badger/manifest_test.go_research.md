<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/badger/manifest_test.go -->
# sources/storage-engines/badger/manifest_test.go

## Purpose
This file tests manifest recovery, corruption detection, rewrite compaction, and concurrent append safety.

## Important APIs, Types, And Functions
`TestManifestBasic` writes data, validates, closes, reopens, and verifies a stored key/user meta. `helpTestManifestFileCorruption` mutates bytes in `MANIFEST` to drive `TestManifestMagic`, `TestManifestVersion`, and `TestManifestChecksum`. `buildTable` constructs temporary tables. `TestManifestRewrite` forces a low deletion threshold and validates the compacted manifest contents. `TestConcurrentManifestCompaction` overrides `syncFunc` to slow syncs and runs concurrent `addChanges` calls.

## Control Flow
The tests create temp DB directories, open/close Badger, mutate manifest files directly for corruption cases, and call `helpOpenOrCreateManifestFile` where needed. Rewrite testing creates a chain of create/delete changes that should collapse to the last live table after reopen. Concurrent testing simulates two compaction threads appending identical change sets behind the manifest append lock.

## State And Persistence Behavior
The tests use actual filesystem manifests and table files. Corruption tests verify startup rejects bad header and checksum state. Rewrite testing checks durable file rewrite and replay state after the manifest was compacted. Concurrent testing validates lock-protected append/rewrite with a real file sync path.

## Dependencies And Integration Points
It depends on `Open`, transaction helpers, table builders, protobuf manifest changes, Badger options, file mutation via `os.OpenFile`, and `syncFunc` injection from `manifest.go`. It validates manifest integration with DB open/reopen and compaction-style changes.

## Risks And Edge Cases
`TestOverlappingKeyRangeError` is skipped and notes that its old premise no longer makes sense. `TestConcurrentManifestCompaction` mutates global `syncFunc` and does not restore it in this file, so test isolation depends on package ordering or later overrides. The corruption helper writes one byte at fixed offsets tied to the current manifest layout.

## Test Signals
Signals include exact error substrings for bad magic/version/checksum, replayed live table map after rewrite, no error from concurrent `addChanges`, and key/value/user-meta survival across reopen.
<!-- END_FILE_RESEARCH: sources/storage-engines/badger/manifest_test.go -->
