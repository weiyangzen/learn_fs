## sources/sync-backup/bup/test/ext/test-import-duplicity

Purpose: integration test for importing duplicity backups.

Important control flow: skips if `duplicity` is unavailable, syncs sample data, creates two duplicity backups with a tick and a new file, runs `bup import-duplicity`, checks save count and latest listing, restores latest, and compares trees. Expected differences allow timestamp and symlink metadata differences.

State and dependencies: writes duplicity cache and backup directory, uses `PASSPHRASE`, Bup import command, restore, and `dev/compare-trees`.

Risks covered: import timeline handling, latest content correctness, and known metadata limitations of duplicity imports.
