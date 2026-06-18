# sources/sync-backup/git-lfs/lfs/util_test.go

Purpose: Tests callback reader accounting and `GitFilter.CopyCallbackFile` progress-log throttling.

Important APIs/types/functions: Uses `tools.NewByteBodyWithCallback`, `tools.CallbackReader`, `GitFilter.CopyCallbackFile`, fake clock, and `tasklog.DefaultLoggingThrottle`.

Control flow: The first two tests read a five-byte payload in two chunks and assert callback counts and cumulative bytes. The throttle test configures `GIT_LFS_PROGRESS`, reads a larger buffer at controlled fake times, and asserts only delayed or final progress lines are written.

State and persistence behavior: Uses a temp progress log file and a fake clock. The callback keeps `prevWritten` and a deadline to suppress too-frequent writes.

Dependencies and integration points: Integrates LFS progress logic with `config.Environment`, `jmhodges/clock`, and `tools.CallbackReader`.

Risks and edge cases: Confirms final completion is logged even before the next throttle interval. It does not cover invalid progress paths, filesystem errors, or nil callback conditions.

Test signals: Good signal for progress log format: `event index/total written/total filename`.
