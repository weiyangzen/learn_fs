# sources/sync-backup/kopia/repo/blob/filesystem/filesystem_options.go

Purpose: defines configuration for filesystem-backed blob storage and helpers for default permissions.

Important APIs/types/functions: `Options`, `fileMode`, and `dirMode`. Options include root path, file/dir modes, optional UID/GID ownership, sharding options, throttling limits, and an unexported OS interface override for tests.

Control flow: `fileMode` returns configured file mode or default `0600`; `dirMode` returns configured directory mode or default `0700`. Validation of path accessibility and directory creation occurs in `filesystem_storage.go`.

State and persistence behavior: exported fields form the persistent JSON config. UID/GID fields allow root-run processes to chown written blobs after atomic rename. The OS override is not serialized and exists for tests.

Dependencies/integration points: consumed by `fsImpl`, sharded storage, throttling wrappers, and repository config. Risks include permission defaults affecting interoperability, zero values meaning defaults so explicit mode `0` cannot be represented, and ownership changes only attempted as root. Tests cover validation, path creation, modes indirectly, and mock OS behavior.
