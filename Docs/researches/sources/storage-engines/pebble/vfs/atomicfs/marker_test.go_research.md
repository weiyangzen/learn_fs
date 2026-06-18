# Research: sources/storage-engines/pebble/vfs/atomicfs/marker_test.go

## Purpose
`vfs/atomicfs/marker_test.go` verifies marker filename parsing, marker movement, obsolete cleanup, crash durability, and fault tolerance under injected filesystem errors.

## Important APIs, Types, And Functions
`TestMarker_FilenameRoundtrip` checks formatting/parsing. `TestMarker_Parsefilename` validates accepted and rejected marker names. `TestMarker` is a datadriven suite with commands `list`, `locate`, `mkdir-all`, `move`, `next-iter`, `read`, `remove-obsolete`, and `touch`. `TestMarker_StrictSync` uses crashable memory FS to verify synced marker survival. `TestMarker_FaultTolerance` injects errors at successive operation counts and retries injected failures once.

## Control Flow
The datadriven test keeps a map of open markers per directory/name, closing prior handles on relocalization. Fault-tolerance testing runs a fixed sequence of locate/move/remove-obsolete operations repeatedly while shifting the injected-error point until no operation is hit; injected errors are retried exactly once.

## State And Persistence
Tests use `vfs.NewMem` and `vfs.NewCrashableMem`. Persistent test state is marker files in memory, open directory handles, and obsolete marker lists. Strict sync tests crash-clone with unsynced data dropped to confirm `Move` and directory syncs are sufficient.

## Dependencies And Integration Points
It integrates datadriven files, `crstrings` line parsing, `errorfs`, crashable VFS behavior, and `require` assertions. It validates the durability primitive used by Pebble MANIFEST markers.

## Risks And Edge Cases
The tests intentionally do not inject sync errors because production treats them as fatal panics. Because marker handles are not concurrent-safe, tests manage one active handle per marker path. Fault-tolerance relies on retrying operations after injected errors and checking the final visible value.

## Test Signals
Signals include correct handling of values containing dots, max uint64 iteration parsing, malformed marker rejection, highest-iteration selection, `NextIter`, obsolete file deletion, crash persistence of moved values, and robustness to create/remove/list/open failures.
