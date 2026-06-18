# sources/sync-backup/syncthing/lib/fs/util.go

## Purpose
Provides path, home-directory, Windows filename, sanitization, parent, and common-prefix helpers shared by filesystem code.

## Important APIs, Types, and Functions
`ExpandTilde`, `getHomeDir`, `WindowsInvalidFilename`, `SanitizePath`, `windowsReservedNamePart`, `IsParent`, `CommonPrefix`, `PathComponents`, and `isVolumeNameOnly`.

## Control Flow
`ExpandTilde` expands `~` and `~/` with Windows historical home handling. Windows validation rejects reserved characters, trailing spaces/periods, and reserved device names per path component. `SanitizePath` collapses invalid characters and whitespace to single spaces and prepends `-` for reserved Windows names. `CommonPrefix` compares cleaned path components while respecting absolute/relative mismatch and Windows volume roots.

## State and Persistence Behavior
Pure helper functions, except environment reads for home directory.

## Dependencies and Integration Points
Used by root normalization, ignore matching, path display/safety, Windows path checks, and case/walk code.

## Risks
`IsParent` is lexical and requires both paths to have matching absolute/relative form. `SanitizePath` is intentionally conservative and may alter valid Unix names to avoid surprising shell or Windows behavior.

## Test Signals
`util_test.go` covers common prefixes, invalid Windows names, sanitization, fuzz-like printable UTF-8 guarantee, and benchmarks.
