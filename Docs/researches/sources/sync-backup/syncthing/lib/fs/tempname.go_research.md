# sources/sync-backup/syncthing/lib/fs/tempname.go

## Purpose
Creates and detects Syncthing temporary filenames in a platform-aware, filename-length-safe way.

## Important APIs, Types, and Functions
Constants `WindowsTempPrefix`, `UnixTempPrefix`, `maxFilenameLength`; functions `tempPrefix`, `IsTemporary`, `TempNameWithPrefix`, and `TempName`.

## Control Flow
`TempName` chooses a Windows or Unix prefix, then `TempNameWithPrefix` prefixes the basename and appends `.tmp`. Long basenames are replaced with a SHA-256 hex digest to stay under conservative filename length limits. `IsTemporary` recognizes both Windows and Unix prefixes regardless of current platform.

## State and Persistence Behavior
Pure string/path generation; no files are created.

## Dependencies and Integration Points
Used by ignore matching to always ignore temp files, Windows 8.3 detection, and file synchronization temp naming.

## Risks
Hashing long basenames loses human readability and theoretically can collide, though SHA-256 makes that negligible. Length limit is conservative to support unusual filesystems.

## Test Signals
`tempname_test.go` validates long-name shortening and short-name suffix behavior; benchmarks measure allocations.
