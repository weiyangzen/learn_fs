## sources/sync-backup/restic/internal/migrations/list.go

Purpose: central migration registry.

Important APIs: package variable `All []Migration` stores registered migrations. `register(m Migration)` appends to it.

Control flow and state: registrations occur through `init` functions in migration implementation files. The order is Go initialization order within the package, so it should remain deterministic for files in the package but should be treated carefully when adding migrations.

Dependencies and integration points: command code enumerates `All`; `upgrade_repo_v2.go` registers itself here.

Risks and test signals: global mutable registration is simple but not concurrency-protected; registrations happen at init time before use. There are no direct registry tests in this target set.
