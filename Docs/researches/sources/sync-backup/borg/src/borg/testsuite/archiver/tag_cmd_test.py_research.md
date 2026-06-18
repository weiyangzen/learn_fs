<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/borg/src/borg/testsuite/archiver/tag_cmd_test.py -->
# sources/sync-backup/borg/src/borg/testsuite/archiver/tag_cmd_test.py

Purpose: local integration tests for `borg tag` operations and special tag safety.

Important APIs: `cmd`, `RK_ENCRYPTION`, tag flags `--set`, `--add`, `--remove`, and `EXIT_ERROR`.

Control flow: creates a repository/archive, then verifies `--set` replaces normal tags and sorts multiple tags; `--add` accumulates tags; `--remove` deletes them. Special tag tests ensure `@PROT` is not accidentally clobbered by `--set` unless included explicitly, and unknown special tags cannot be set, added, or removed.

State and persistence: archive metadata tags mutate in the repository manifest/archive record.

Dependencies/integration: depends on local archiver only, tag formatting, protected tag semantics, and special-tag validation. Risks include accidental removal of protection tags. Test signals are exact output fragments and expected error exits.
<!-- END_FILE_RESEARCH: sources/sync-backup/borg/src/borg/testsuite/archiver/tag_cmd_test.py -->
