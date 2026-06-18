# sources/sync-backup/syncthing/lib/fs/mtimefs.go

## Purpose
Adds virtual nanosecond modification-time support over filesystems that may round or fail `Chtimes`.

## Important APIs, Types, and Functions
`database` interface, `mtimeFS`, `MtimeFSOption`, `WithCaseInsensitivity`, `optionMtime`, `NewMtimeOption`, `mtimeFileInfo`, `mtimeFile`, and `GetMtimeMapping`.

## Control Flow
`Chtimes` attempts the underlying change, then stats the file and stores the real on-disk mtime plus requested virtual mtime. `Stat`, `Lstat`, and file `Stat` replace `ModTime` with the virtual value only when current disk mtime equals the saved on-disk value. Equal real/virtual mtimes delete the DB mapping.

## State and Persistence Behavior
Persists mtime mappings in the supplied database keyed by folder ID and normalized name when configured case-insensitive. The filesystem itself may or may not store the requested exact timestamp.

## Dependencies and Integration Points
Applied by `NewFilesystem` before walking. Integrates with `walkFilesystem`, `casefs`, and copy-range unwrapping.

## Risks
Database errors in save/delete are ignored. If on-disk mtime changes externally, virtual mtime is no longer applied. Case-insensitive mapping must match underlying filesystem behavior to avoid misses.

## Test Signals
`mtimefs_test.go` covers failed/evil `Chtimes`, walk and open stat behavior, underlying mtime divergence, and case-insensitive mapping.
