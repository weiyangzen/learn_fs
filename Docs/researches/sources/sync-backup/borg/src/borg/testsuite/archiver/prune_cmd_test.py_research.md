<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/borg/src/borg/testsuite/archiver/prune_cmd_test.py -->
# sources/sync-backup/borg/src/borg/testsuite/archiver/prune_cmd_test.py

Purpose: broad prune coverage for CLI retention behavior plus unit-level tests of `prune_within` and `prune_split`.

Important APIs: `cmd`, `_create_archive_ts`, `prune_within`, `prune_split`, `interval`, `MockArchive`, retention flags (`--keep-daily`, `--keep-monthly`, quarterly variants, etc.), and archive match filters.

Control flow: CLI tests create timestamped archives and run dry-run and real `prune`, checking kept/pruned output and subsequent `repo-list` state. The documented prune example, quarterly strategies, oldest-retention expiration, prefix/glob matching, protected archive ignoring, metadata-format listing, and JSON/list-pruned schemas are covered. Unit tests build `MockArchive` instances in local timezone and assert selected archive IDs and `kept_because` rule labels.

State and persistence: archive metadata timestamps are deliberately controlled; real prune mutates repository archive visibility. Protected tags prevent deletion. Local timezone is captured because prune converts archive timestamps to local time.

Dependencies/integration: depends on CLI output wording, local timezone handling, retention bucket algorithms, archive matching, JSON schema, and tag semantics. Risks include date math edge cases, dry-run accidentally mutating state, and formatting lazy-load regressions after deletion. Test signals are regex matches, repository listings, JSON fields, and exact kept sets.
<!-- END_FILE_RESEARCH: sources/sync-backup/borg/src/borg/testsuite/archiver/prune_cmd_test.py -->
