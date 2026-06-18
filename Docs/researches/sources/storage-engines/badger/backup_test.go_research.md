# sources/storage-engines/badger/backup_test.go

Purpose: verifies backup/restore correctness across disk and memory modes, incremental streams, metadata handling, and transaction timestamp restoration.

Important tests: `TestBackupRestore1/2/3` write data, back it up, load it into new DBs, and assert keys, values, versions, user metadata, and `nextTs`. `TestBackup` checks basic backup in disk and in-memory configurations. `TestBackupLoadIncremental` applies deletes, expired entries, and discard-earlier-version entries between incremental backups, then checks restored historical/deleted metadata. `TestBackupBitClear` ensures backup/restore clears value-pointer bits when source and destination value thresholds differ.

State and persistence: tests create temp directories/files and remove them through helpers; they exercise both on-disk state and in-memory DB mode. Dependencies are `testing`, `require`, `pb.KV`, and Badger test helpers. Risks: randomized selection uses package-level `randSrc`, so exact updated indexes vary; some tests print lengths to stdout; concurrent restore assumptions are not stress-tested. Test signals are strong for functional backup semantics but weaker for corrupted backup input, huge record sizes, writer failures, and concurrent restore misuse.
