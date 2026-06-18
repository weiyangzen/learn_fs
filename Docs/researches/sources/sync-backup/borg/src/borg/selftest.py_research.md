# sources/sync-backup/borg/src/borg/selftest.py

Purpose: runs Borg's small built-in self-test suite through `unittest`, without requiring pytest for end users.

Important APIs/types: `SELFTEST_CASES`, `SELFTEST_COUNT`, `SelfTestResult`, and `selftest(logger)`. `SelfTestResult` tracks successes, logs errors/failures/unexpected successes/skips, and counts successful tests.

Control flow/state: `selftest` returns early when `BORG_SELFTEST=disabled`; otherwise it builds a `TestSuite`, asserts imported self-test modules do not import pytest, runs tests, logs failures/skips, checks success count against `SELFTEST_COUNT`, exits with code 2 on failure or count mismatch, and logs elapsed time on success.

Dependencies/integration: imports selected crypto and chunker self-test classes and expects a configured Borg logger. Used as a process-level health gate.

Risks: `SELFTEST_COUNT` must be maintained with test changes. Any failure terminates the process. Imported test modules must stay pytest-free and lightweight.

Test signals: disabled env behavior, success path, count mismatch, pytest import assertion, skip/failure logging, and exit code 2.
