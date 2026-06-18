# sources/sync-backup/syncthing/lib/fs/filesystem.go

## Purpose
Defines Syncthing's filesystem abstraction and factory/wrapper construction pipeline, plus shared path, event, error, and utility helpers.

## Important APIs, Types, and Functions
Interfaces and types: `Filesystem`, `File`, `FileInfo`, `XattrFilter`, `Matcher`, `Event`, `EventType`, `Usage`, `FileMode`, and `wrappingFilesystem`. Functions include `NewFilesystem`, `IsInternal`, `Canonicalize`, `unwrapFilesystem`, and `WriteFile`. Constants mirror `os` modes/open flags and standard errors.

## Control Flow
`NewFilesystem` extracts case and mtime options, constructs the registered base filesystem or `errorFilesystem`, applies `mtimeFS`, wraps metrics, applies walk/log wrappers based on debug settings, then applies case detection outermost. `Canonicalize` cleans paths, rejects upward traversal, strips leading root separators, and maps root to `"."`.

## State and Persistence Behavior
Global factory registry stores filesystem type constructors. `WriteFile` writes data by truncating/creating a file and can leave partial data on mid-write failures. `NewFilesystem` wrapper choices affect runtime behavior but do not persist.

## Dependencies and Integration Points
Central integration point for `basic`, `fake`, `walkfs`, `metrics`, `logfs`, `mtimefs`, `casefs`, ignore matching, and protocol platform data.

## Risks
Wrapper ordering is subtle and safety-critical. `WriteFile` is non-atomic. `Canonicalize` treats absolute-looking paths as root-relative except double separators, so callers must understand this contract.

## Test Signals
`filesystem_test.go` covers internal names, canonicalization, `FileMode.String`, parent logic, and a regression for caseFS/mtimeFS wrapper caching.
