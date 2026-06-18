# sources/sync-backup/syncthing/lib/syncthing/internals.go

Purpose: exposes a deliberately unstable but narrower API over `model.Model` for direct package consumers, including mobile apps.

Important APIs and control flow: `Internals` stores `model.Model`. Methods forward to model operations for folder state, ignores, block download, availability, global file info/tree, connectivity, scans, completion, device stats, pending folders, subdirectory scans, global/local/need sizes, all global files, progress bytes, need-file pagination, remote need files, and local changed files. `Counts` aliases `db.Counts`.

State and persistence: no state beyond the model reference. Persistence and locks are owned by the underlying model/database.

Dependencies and integration: created in `App.startup` after `model.NewModel`. Integrates `db`, `protocol`, `stats`, and `model` types into an importable boundary.

Risks: because it forwards directly, model behavior changes can affect external consumers despite the intended boundary. No validation is added here; errors propagate as-is. No tests in this subset.
