# sources/sync-backup/kopia/repo/initialize.go

Purpose: builds initial repository format structures and calls `format.Initialize` to create a new Kopia repository in blob storage.

Important APIs/types/functions: `NewRepositoryOptions`, `Initialize`, `formatBlobFromOptions`, `blobCfgBlobFromOptions`, `repositoryObjectFormatFromOptions`, and default helpers for ints, strings, ranges, and random bytes.

Control flow: `Initialize` normalizes nil options, creates the format blob, blob retention configuration, and repository config, validates/adjusts format-version-dependent fields, then delegates to the format package with the password. Repository config defaults include hashing, encryption, ECC, pack/index version, splitter, HMAC secret, and master key.

State/persistence behavior: writes initial repository metadata to the supplied blob storage. It generates unique IDs, HMAC secrets, and master keys when not provided; disabling HMAC clears the secret. Format version 1 or zero ECC overhead disables ECC fields.

Dependencies/integration: integrates blob storage, content defaults, format version resolution, encryption, ECC, hashing, and splitter defaults.

Risks/test signals: random generation errors are ignored in helpers, so entropy-source failures would silently produce zeroed bytes. Format compatibility depends on default constants and `ResolveFormatVersion`. Tests for these defaults are indirect through repository integration suites.
