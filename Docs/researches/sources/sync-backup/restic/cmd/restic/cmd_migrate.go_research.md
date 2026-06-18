# sources/sync-backup/restic/cmd/restic/cmd_migrate.go

Purpose: implements `restic migrate`, listing available migrations or applying named migrations to a repository.

Important APIs/types/functions: `MigrateOptions`; `checkMigrations`; `applyMigrations`; `runMigrate`.

Control flow and state: `runMigrate` opens an exclusive lock. With no args it checks each `migrations.All` entry and prints applicable migrations. With names, it matches each migration, checks applicability, optionally continues with `--force`, runs repository integrity checks for migrations requiring them with `NoLock` because the exclusive lock is already held, applies the migration, prints status, and returns the first apply error after trying remaining migrations.

Dependencies and integration points: depends on `internal/migrations`, `runCheck`, restic repository interfaces, and progress output.

Risks: unknown migration names only print an error and do not affect `firsterr`. Forced migrations can run despite failed prechecks. RepoCheck migrations invoke a full check before mutation.

Test signals: no file-specific tests in this shard; coverage likely comes from migration package tests and command flag parsing.
