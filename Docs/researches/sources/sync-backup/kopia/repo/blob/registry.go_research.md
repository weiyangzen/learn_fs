# sources/sync-backup/kopia/repo/blob/registry.go

Purpose: provides the global registry from storage type names to provider factory functions.

Important APIs/types/functions: global `factories`, `storageFactory`, `AddSupportedStorage`, and `NewStorage`.

Control flow: provider packages call generic `AddSupportedStorage` from `init`, supplying a type name, default config value, and typed create function. The registry stores a default-config function and an untyped create wrapper with a type assertion. `NewStorage` looks up the config type and invokes the factory or returns an unknown type error.

State and persistence behavior: registry state is process-global and populated at package initialization. It is not persisted, but it interprets persisted `ConnectionInfo` types.

Dependencies/integration points: central to all blob providers and `ConnectionInfo.UnmarshalJSON`. Risks include no locking around registration, duplicate type names overwriting previous factories, type assertions panicking if config does not match, and unknown types when provider packages are excluded by build tags. Tests cover registering a custom storage and connection info behavior.
