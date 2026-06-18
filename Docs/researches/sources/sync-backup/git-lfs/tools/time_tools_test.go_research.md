# sources/sync-backup/git-lfs/tools/time_tools_test.go

Purpose: tests expiration helper precedence and boundary behavior.

Important APIs/types/functions: tests for `TimeAtOrIn` and `IsExpiredAtOrIn`.

Control flow: constructs `now`, absolute `at`, and relative `in` combinations, then asserts chosen expiration and expired boolean.

State and persistence: no I/O; uses current wall-clock time in test setup.

Dependencies and integration points: validates transfer action expiry behavior indirectly.

Risks: comparisons are exact for values derived from the same `now`, but tests involving `time.Now()` inside implementation could be sensitive near boundaries.

Test signals: good coverage of intended precedence, especially relative duration winning over absolute time.
