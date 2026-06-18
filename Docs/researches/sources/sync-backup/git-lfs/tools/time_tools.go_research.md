# sources/sync-backup/git-lfs/tools/time_tools.go

Purpose: helpers for handling absolute and relative expiration times.

Important APIs/types/functions: `IsExpiredAtOrIn` and `TimeAtOrIn`.

Control flow: `TimeAtOrIn` prefers a relative duration when non-zero, otherwise returns an absolute time. `IsExpiredAtOrIn` computes expiration and compares it to `time.Now().Add(until)`, treating zero time as non-expiring.

State and persistence: no persistent state; uses wall-clock time.

Dependencies and integration points: `tq.Action.IsExpiredWithin` uses this to decide whether transfer actions should be retried before expiry.

Risks: wall-clock dependency can make boundary behavior time-sensitive; when both `at` and `in` are provided, `in` wins.

Test signals: `time_tools_test.go` covers absolute, relative, zero, expired, and ambiguous cases.
