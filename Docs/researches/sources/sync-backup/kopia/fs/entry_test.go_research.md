<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/kopia/fs/entry_test.go -->
# sources/sync-backup/kopia/fs/entry_test.go

## Purpose
Unit tests for entry sorting and sorted lookup helpers.

## Important APIs, Types, And Functions
Defines a lightweight `testEntry` with a `Name` method and embedded `Entry`, then tests `FindByName` and `Sort`.

## Control Flow
`TestEntriesFindByName` searches a sorted slice for an existing name and several missing positions. `TestEntriesSort` sorts unsorted entries and compares against expected order using pretty diff.

## State And Persistence Behavior
No persistent state is involved.

## Dependencies And Integration Points
Integrates fs helper functions and the `godebug/pretty` diff library.

## Risks And Edge Cases
The lookup test assumes input is sorted, matching the helper contract. It does not test duplicate names or unsorted lookup failure modes.

## Test Signals
Good low-level signal for name ordering helpers used by virtual filesystem and snapshot traversal code.
<!-- END_FILE_RESEARCH: sources/sync-backup/kopia/fs/entry_test.go -->
