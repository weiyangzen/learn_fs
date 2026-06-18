# sources/storage-engines/badger/badger/cmd/backup.go

Purpose: implements the `badger backup` CLI command over the library `DB.Backup` API.

Important flow: Cobra registers flags `--backup-file/-f` and `--num-versions/-n`. `doBackup` opens Badger with `DefaultOptions(sstDir)`, `WithValueDir(vlogDir)`, and `WithNumVersionsToKeep(math.MaxInt32)` unless the flag narrows retention. It creates the backup file, wraps it in a 64 MiB buffered writer, runs `db.Backup(bw, 0)`, flushes, fsyncs the file, and closes it.

State and persistence: persistent output is the backup file; source DB is opened read-write by default through `badger.Open`. Dependencies are root command directory validation, Badger options, filesystem create/sync, and buffered I/O. Risks: source DB is not opened read-only, partial files can remain on failure, and close errors can mask earlier sync/flush context only by direct return order. Test signals should cover CLI backup/restore round trips, num-version effects, write permission failures, and backup over separate `--vlog-dir`.
