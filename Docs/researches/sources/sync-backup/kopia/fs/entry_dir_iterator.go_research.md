<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/fs/entry_dir_iterator.go -->
# sources/sync-backup/kopia/fs/entry_dir_iterator.go

## Purpose
Provides a simple static `DirectoryIterator` implementation over a prebuilt entry slice and optional final error.

## Important APIs, Types, And Functions
Defines `staticIterator`, methods `Close` and `Next`, and constructor `StaticIterator`.

## Control Flow
`Next` returns entries in order while `cur < len(entries)`, incrementing each time. It returns the configured `err` alongside each entry, then returns `(nil, nil)` after all entries are consumed.

## State And Persistence Behavior
No persistent state exists beyond iterator position in memory.

## Dependencies And Integration Points
Integrates the `DirectoryIterator` interface from `entry.go` and is useful for virtual or test directories.

## Risks And Edge Cases
Returning `it.err` with every entry is unusual because the iterator contract treats `(entry,nil)` as success and `(nil,err)` as failure. Callers that stop on nonnil error may ignore returned entries when `err` is set.

## Test Signals
Tests should cover normal iteration, empty slices, configured error semantics, and Close idempotence.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/fs/entry_dir_iterator.go -->
