# sources/sync-backup/kopia/repo/blob/rclone/rclone_options.go

Purpose: defines persistent options for the rclone-backed storage provider.

Important APIs/types/functions: `Options` with remote path, rclone executable, extra args/env, startup timeout, debug flag, close-transfer behavior flag, embedded config, atomic write flag, sharded options, and throttling limits.

Control flow: no functions are in this file. `rclone_storage.go` interprets these options to launch `rclone serve webdav` and connect through the WebDAV provider.

State and persistence behavior: options are serialized in repository config. `EmbeddedConfig` may contain credentials but is not marked sensitive in this file, which is a notable risk.

Dependencies/integration points: consumed by rclone provider creation, WebDAV options, sharding, throttling, and JSON duration handling. Risks include command-line/env injection through user-controlled options, provider warning about limited testing/data loss, and `NoWaitForTransfers` existing in options but not used in the shown close path. Tests cover invalid executable/flags, providers, cancel context, directory shards, and shared behavior.
