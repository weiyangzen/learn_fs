# sources/sync-backup/syncthing/lib/config/pullorder.go

## sources/sync-backup/syncthing/lib/config/pullorder.go

Purpose: Defines folder pull order configuration text values.

Important APIs/types/functions: `PullOrder` enum supports random, alphabetic, smallest-first, largest-first, oldest-first, and newest-first. It implements `String`, `MarshalText`, and `UnmarshalText`.

Control flow and state: Unknown text defaults to random. Unknown enum values stringify as `unknown`.

Dependencies and integration: Used by `FolderConfiguration.Order` to control file pull scheduling.

Risks and test signals: Invalid config silently becomes random. `TestPullOrder` loads all supported values plus an unknown value from `pullorder.xml`, then verifies XML round-trip preservation of supported values.
