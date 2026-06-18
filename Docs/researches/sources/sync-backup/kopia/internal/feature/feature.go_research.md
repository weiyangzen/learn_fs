# sources/sync-backup/kopia/internal/feature/feature.go

Purpose: models repository/client feature compatibility and produces user-facing messages when a client does not understand a required feature.

Important APIs/types/functions: `IfNotUnderstood`, `Feature`, `Required`, `Required.UnsupportedMessage`, `GetUnsupportedFeatures`, and `isSupported`. JSON tags indicate these structures are serialized in repository metadata or manifests.

Control flow: `GetUnsupportedFeatures` iterates required features and appends those absent from the supported feature slice. `UnsupportedMessage` composes a base message with optional custom text, documentation URL, and upgrade recommendation.

State/persistence behavior: the package has no mutable runtime state. Persistence concerns are in the JSON shape, especially optional fields under `IfNotUnderstood`.

Dependencies/integration: uses `slices.Contains` for feature membership. Upstream code can fail, warn, or guide upgrades based on returned unsupported `Required` values.

Risks/test signals: matching is exact string equality with no version ranges or aliases. `IfNotUnderstood.Warn` is stored but not interpreted here, so callers must enforce warning-versus-failure behavior.
