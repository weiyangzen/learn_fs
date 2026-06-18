<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/borg/src/borg/testsuite/archiver/repo_info_cmd_test.py -->
# sources/sync-backup/borg/src/borg/testsuite/archiver/repo_info_cmd_test.py

Purpose: tests `borg repo-info` text and JSON output for repository metadata.

Important APIs: `cmd`, `create_regular_file`, `checkts`, JSON parsing, and `RK_ENCRYPTION`.

Control flow: both tests create a repository and archive. The text test checks that `Repository ID:` appears. The JSON test parses `repo-info --json`, validates a 64-character repository ID, `last_modified` timestamp parseability, encryption mode matching the configured repokey mode, and absence of a keyfile field for repokey storage.

State and persistence: repository and archive metadata are persisted before inspection.

Dependencies/integration: depends on JSON schema, timestamp formatting, and encryption mode reporting. Risks include schema drift or incorrect exposure of keyfile details. Test signals are text containment and JSON field checks.
<!-- END_FILE_RESEARCH: sources/sync-backup/borg/src/borg/testsuite/archiver/repo_info_cmd_test.py -->
