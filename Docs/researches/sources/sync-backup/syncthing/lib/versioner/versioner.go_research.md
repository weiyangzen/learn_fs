# Research: sources/sync-backup/syncthing/lib/versioner/versioner.go

## sources/sync-backup/syncthing/lib/versioner/versioner.go

Purpose: defines the common file versioning interface and factory registry used by concrete Syncthing versioners.

Important APIs/types/functions: `Versioner` exposes `Archive`, `GetVersions`, `Restore`, and `Clean`; `FileVersion` is the JSON-facing version metadata tuple of `VersionTime`, `ModTime`, and `Size`; `New` looks up `factories[cfg.Versioning.Type]`; `ErrRestorationNotSupported`, `TimeFormat`, and `timeGlob` standardize error and timestamp handling.

Control flow: concrete versioner packages register a `factory` in the package-level `factories` map. `New` fails for unknown type, otherwise wraps the concrete implementation in `versionerWithErrorContext`. The wrapper preserves behavior but annotates operation failures with versioner type and operation name.

State and persistence: this file owns no persistent state. The registry is in-process package state, while concrete implementations own filesystem persistence.

Dependencies and integration: integrates with `config.FolderConfiguration` and downstream versioner implementations. Risks are global registry mutation order and error wrapping expectations in callers. Test signals come from concrete versioner tests that call `New` and assert archive/restore semantics.
