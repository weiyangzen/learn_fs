# Research: sources/storage-engines/pebble/version_set_test.go

## Purpose
`version_set_test.go` validates `versionSet` behavior through datadriven manifest edits, checkpoint/reopen scenarios, sequence-number accounting, large keys, and crash recovery during manifest writes.

## Important APIs, Types, And Functions
`writeAndIngest` builds a one-key external SSTable and ingests it. `TestVersionSet` drives `versionSet.UpdateVersionLocked` directly with parsed debug edits and commands for protecting backings, holding version refs, reopening, and printing metrics. `TestVersionSetCheckpoint` verifies manifest rotation preserves state. `TestVersionSetSeqNums` checks `LastSeqNum` in the active manifest. `TestLargeKeys` exercises DB operations and sstable layout/properties with huge shared-prefix keys. `TestCrashDuringManifestWrite_LargeKeys` simulates crashes during manifest writes with crashable memory FS clones.

## Control Flow
The main datadriven test initializes an in-memory version set with value separation enabled, parses each edit, normalizes/deduplicates table backings, creates physical files for non-virtual backings, resolves deleted table/blob metadata, applies the edit under the DB mutex, and prints current version, virtual backing state, zombie objects, and obsolete files. Reopen commands recover from the manifest and rebuild lookup maps.

## State And Persistence
Tests use in-memory or crashable VFS instances and object stores. They persist MANIFEST records, marker files, table objects, and ingested SSTables within test filesystems. Some tests intentionally hold version references to keep deleted objects zombie rather than obsolete.

## Dependencies And Integration Points
The file integrates manifest debug parsing, object storage provider, atomic manifest markers, record readers, errorfs injection, testkey comparers, external ingestion, DB open/close/recovery, and CLI-style helper commands for layout/properties.

## Risks And Edge Cases
The datadriven harness must manually keep metadata maps consistent with parsed edits. Randomized forced manifest rotation broadens coverage but requires deterministic output cleanup such as zeroing `NextFileNum`. Crash tests use randomness and can reveal multi-block record decoding problems. Large-key tests protect against separator-shortening assumptions in index and manifest logic.

## Test Signals
Signals include exact current-version debug strings, virtual backing state, zombie/obsolete object lists, metrics output, successful reopen after repeated rotations, manifest `LastSeqNum == logSeqNum-1`, stable large-key layout/properties output, and successful open after crash-cloned partial manifest writes.
