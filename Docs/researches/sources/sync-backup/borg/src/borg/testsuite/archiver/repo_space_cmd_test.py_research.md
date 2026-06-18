<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/borg/src/borg/testsuite/archiver/repo_space_cmd_test.py -->
# sources/sync-backup/borg/src/borg/testsuite/archiver/repo_space_cmd_test.py

Purpose: tests `borg repo-space` reserved-space management.

Important APIs: `cmd`, `generate_archiver_tests`, `RK_ENCRYPTION`, and repo-space flags `--reserve`/`--free`.

Control flow: tests create repositories, query initial reservation, reserve sizes such as `100M`, `50M`, `0`, and `1K`, assert human-readable rounded output, and free reserved space. The modify test verifies reservation can increase but not implicitly decrease.

State and persistence: repository reserved-space objects are created and removed; tests free reservations at the end to conserve tmp space.

Dependencies/integration: depends on 64 MiB reservation block rounding and output formatting using decimal MB. Risks include brittle exact strings if formatter units change and disk usage during tests. Test signals are exact output messages.
<!-- END_FILE_RESEARCH: sources/sync-backup/borg/src/borg/testsuite/archiver/repo_space_cmd_test.py -->
