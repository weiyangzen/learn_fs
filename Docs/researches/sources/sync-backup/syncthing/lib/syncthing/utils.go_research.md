# sources/sync-backup/syncthing/lib/syncthing/utils.go

Purpose: startup utilities for directories, certificates, default/config loading, config archiving, database opening, and LevelDB-to-SQLite migration.

Important APIs and control flow: `EnsureDir` creates a basic filesystem root and corrects permissions best-effort. `LoadOrGenerateCertificate` falls back to `GenerateCertificate`, which uses `tlsutil.NewCertificate`. `DefaultConfig` builds config, optionally probes free ports, and wraps it. `LoadConfigAtStartup` creates a default config when missing, rejects truncated config, archives/saves when version changes, and can reject newer configs unless allowed. `OpenDatabase` opens SQLite with delete retention and metrics wrapping. `TryMigrateDatabase` detects legacy LevelDB, opens SQLite migration DB, skips already-migrated DBs, iterates folders and file snapshots, writes batches of 1000 local file infos while applying delete retention, migrates mtimes, records migration metadata, and renames the old DB directory.

State and persistence: writes certificate/key files, config files and archives, SQLite DB content, migration metadata, and renames legacy DB directory.

Dependencies and integration: called by command startup before constructing `App`; integrates locations, fs, config, events, db/sqlite, olddb, backend, protocol, TLS.

Risks: migration is long-running and partially logs progress; failures can leave partial SQLite content before retry. `archiveAndSaveConfig` copies then saves, so archive cleanup on copy write failure is explicit. No tests in this subset.
