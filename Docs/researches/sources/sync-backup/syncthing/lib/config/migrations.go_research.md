# sources/sync-backup/syncthing/lib/config/migrations.go

## sources/sync-backup/syncthing/lib/config/migrations.go

Purpose: Maintains ordered in-place migrations from older Syncthing config versions to `CurrentVersion`.

Important APIs/types/functions: `migrationSet`, `migration`, global `migrations`, and `migrationsMut`. `migrationSet.apply` sorts by target version, then `migration.apply` runs conversion when `cfg.Version` is below the target and updates the version. Specific migrations handle reconnect interval changes, max concurrent writes defaults, pending-device cleanup, junction defaults, notifications, crash reporting, watcher delays, versioning fields, filesystem type, marker upgrades, symlink cleanup, minimum disk free conversion, NAT/relay/listen address migration, discovery URLs, folder type migration, and old TCP address schema.

Control flow and state: Migrations mutate the passed `Configuration`. Some migrations are pure field rewrites; others touch filesystem state (`migrateToConfigV23` marker replacement and `migrateToConfigV21` symlink cleanup). Nil migration entries still advance version because external database migrations may key off config version.

Dependencies and integration: Called by `Configuration.prepare` under a mutex after defaults and option preparation. Uses `fs`, `netutil`, `upgrade`, environment variable `STNOUPGRADE`, URL/path helpers, logging, and build/runtime state. Fixtures `v5.xml`, `v22.xml`, `example.xml`, and targeted issue files exercise the chain.

Risks and test signals: Migration order and idempotence are high risk because every load of an old config depends on it. Filesystem-touching migrations must avoid data loss. Tests cover crash-reporting migration, reconnect interval migration, v14 listen/relay behavior, historical fixture migration, versioning parameter moves, and address trimming/order behavior.
