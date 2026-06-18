<!-- BEGIN_FILE_RESEARCH: sources/sync-backup/git-annex/debian/tests/basics -->
# sources/sync-backup/git-annex/debian/tests/basics

Purpose: autopkgtest smoke test for the Debian package.

Control flow: creates a temporary directory with `mktemp -d`, changes into it, and `exec`s `git-annex test`. Using `exec` makes the test process become the git-annex test command, so its exit code is the autopkgtest result.

State and persistence: the temporary directory is not explicitly removed because the process is replaced by `git-annex test`; cleanup depends on the test harness or filesystem policy.

Dependencies and integration points: requires `/bin/sh`, `mktemp`, a working packaged `git-annex`, and any runtime dependencies needed by the built-in test suite.

Risks: no trap cleanup and no environment isolation beyond a temp working directory. Failures can come from broad git-annex test dependencies rather than only package installation problems.

Test signals: passing autopkgtest is a high-level package health signal. Additional checks could assert the temp directory location and ensure required tools are in `PATH`.
<!-- END_FILE_RESEARCH: sources/sync-backup/git-annex/debian/tests/basics -->
