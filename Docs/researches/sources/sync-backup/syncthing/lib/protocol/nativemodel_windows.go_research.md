# sources/sync-backup/syncthing/lib/protocol/nativemodel_windows.go

## Purpose
Windows-specific raw model wrapper that converts incoming slash-separated wire paths to native backslash paths and rejects peer-supplied names that already contain backslashes. This prevents ambiguous or hostile path separators from entering local model logic.

## Important APIs, Types, and Functions
`makeNative` wraps a `rawModel` in `nativeModel`. `nativeModel.Index` and `IndexUpdate` call `fixupFiles`. `nativeModel.Request` rejects names containing `\` with `ErrNoSuchFile`, otherwise rewrites with `filepath.FromSlash`. `fixupFiles` filters invalid `FileInfo` entries and converts valid names.

## Control Flow
Index processing scans files in order. If no invalid name appears, it mutates the original slice and returns it. On the first invalid name, it lazily allocates an output slice containing earlier valid entries, skips invalid entries, appends later valid converted entries, and returns the filtered slice. Deleted invalid entries are logged at debug level; non-deleted invalid entries are logged as errors. Requests with backslashes are dropped before delegation.

## State and Persistence Behavior
No durable state exists. The code mutates `FileInfo.Name` in memory and may return either the original slice or a filtered copy. Filtering invalid non-deleted entries means remote index state is intentionally not accepted locally.

## Dependencies and Integration Points
Build-tagged for Windows; imports `filepath`, `strings`, `log/slog`, and `internal/slogutil`. It integrates with `NewConnection`'s model wrapper chain and with protocol filename validation, which treats backslash as legal on the wire for non-Windows peers but not acceptable as a Windows path separator.

## Risks and Edge Cases
Callers must handle a returned slice that may be shorter than input. The lazy-copy path must preserve earlier valid entries exactly, and tests cover that. Rejecting requests as `ErrNoSuchFile` hides invalid-separator details from peers but is safer than trying to normalize malicious input.

## Test Signals
`nativemodel_windows_test.go` covers mixed valid, invalid, and deleted-invalid entries, expecting invalid entries to be dropped and slashes converted to backslashes.
