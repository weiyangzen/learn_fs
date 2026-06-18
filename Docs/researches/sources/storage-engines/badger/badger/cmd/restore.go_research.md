# sources/storage-engines/badger/badger/cmd/restore.go

Purpose: implements the `badger restore` CLI command over `DB.Load`.

Important flow: flags configure backup file path and max pending writes. `doRestore` first rejects restoring into a DB directory that already has a manifest. It opens a new Badger DB with `WithNumVersionsToKeep(math.MaxInt32)` and `WithValueDir(vlogDir)`, opens the backup file, and calls `db.Load(f, maxPendingWrites)`.

State and persistence: creates a new Badger DB under `--dir`/`--vlog-dir` and populates it from backup stream data. Dependencies are root command directory validation, filesystem stat/open, Badger open, and backup stream format. Risks: only manifest presence is checked, so non-empty directories without a manifest may still be used; partial restore can leave a DB behind on failure; restore is not designed for concurrent transactions. Test signals are backup/restore CLI round trips, existing-manifest rejection, corrupted backup input, and max-pending-writes behavior.
