# sources/sync-backup/syncthing/lib/versioner/debug.go

Purpose: package logger adapter for file versioning.

Important APIs and control flow: initializes `l` with `slogutil.NewAdapter("File versioning")`.

State and persistence: logger only.

Dependencies and integration: used by simple, staggered, trashcan, external, and helper cleanup paths for diagnostics.

Risks and test signals: no behavior beyond logging setup.
