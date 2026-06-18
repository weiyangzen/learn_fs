<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/borg/src/borg/testsuite/archiver/undelete_cmd_test.py -->
# sources/sync-backup/borg/src/borg/testsuite/archiver/undelete_cmd_test.py

Purpose: tests logical archive undeletion via `borg undelete`.

Important APIs: `cmd`, `create_regular_file`, `RK_ENCRYPTION`, and archive selection with `-a sh:*`.

Control flow: tests create normal and deleted archives, run `delete`, verify deleted archives disappear from normal `repo-list`, then call `undelete` either by exact name, dry-run/list mode, or real multi-archive mode. Final listings verify whether archives returned.

State and persistence: archive deletion is logical/recoverable; undelete flips deleted archives back to visible. Dry-run must not mutate state.

Dependencies/integration: depends on archive deleted-state storage, matching, listing, and repository check after undelete. Risks include confusing dry-run output comments and accidentally undeleting non-candidates. Test signals are output membership and `check` success.
<!-- END_FILE_RESEARCH: sources/sync-backup/borg/src/borg/testsuite/archiver/undelete_cmd_test.py -->
