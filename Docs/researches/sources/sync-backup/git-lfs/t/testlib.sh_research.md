<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-lfs/t/testlib.sh -->
# sources/sync-backup/git-lfs/t/testlib.sh

Purpose: minimal TAP-style shell test harness for Git LFS integration scripts.

Important APIs/functions: defines `atexit`, `begin_test`, and `end_test`; sources `testenv.sh`; calls `setup`, `shutdown`, and `tap_show_plan`.

Control flow: on load it sets strict mode, installs an exit trap, runs shared setup, reads server URLs, and changes to `TRASHDIR`. `begin_test` closes any previous test, increments counters, redirects stdout/stderr/trace to files, resets fake HOME from `TESTHOME`, and disables immediate shell exit so the subshell can report status. `end_test` restores fds, closes trace, prints `ok`/`not ok`, dumps logs on failure or when requested, and clears the current description. `atexit` prints the TAP plan, shuts down, and exits nonzero if failures occurred.

State and persistence: maintains process globals `tests`, `failures`, `test_description`, log files under `TRASHDIR`, fake HOME, and optional Git trace fd.

Dependencies and integration points: integrates with `testenv.sh`, `testhelpers.sh`, Git trace, TAP consumers, lfstest server lifecycle, and every shell test file.

Risks: harness misreporting can hide failures. Because tests must run assertions in `set -e` subshells, missing `set -e` inside blocks can cause false positives.

Test signals: indirectly exercised by all shell tests and visible through TAP output plus dumped stdout/stderr/trace on failure.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-lfs/t/testlib.sh -->
