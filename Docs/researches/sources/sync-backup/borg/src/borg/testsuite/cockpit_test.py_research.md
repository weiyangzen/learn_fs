<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/borg/src/borg/testsuite/cockpit_test.py -->
# sources/sync-backup/borg/src/borg/testsuite/cockpit_test.py

Purpose: slow optional UI integration test for the Textual-based Borg cockpit app running a create command.

Important APIs: optional import `BorgCockpitApp`, `asyncio.run`, Textual `run_test`, subprocess `borg repo-create`, platform flags `is_freebsd`/`is_win32`, and app fields `borg_args`, `process_running`, `total_lines_processed`, and `#status`.

Control flow: module-level skip applies if cockpit/Textual is unavailable. The test further skips except on FreeBSD or Windows, creates a repo and 5000 input files, initializes an unencrypted repository via subprocess, then runs the cockpit app test harness with `borg create --list`. It waits until the process finishes, asserts status return code 0, line processing occurred, and quits with `q`.

State and persistence: creates many temporary files and a temporary repository; drives an async UI app in test mode.

Dependencies/integration: depends on installed `borg` command, Textual app importability, platform-specific need for slow UI coverage, and async process state updates. Risks include long runtime, UI selector drift, subprocess PATH issues, and polling loop hangs if process state is not updated. Test signals are app title/running state, status panel return code, and processed-line count.
<!-- END_FILE_RESEARCH: sources/sync-backup/borg/src/borg/testsuite/cockpit_test.py -->
