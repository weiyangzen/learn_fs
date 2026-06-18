# sources/sync-backup/casync/src/time-util.h

Purpose: defines time constants and inline conversion helpers.

Important APIs/types/functions: declares nanosecond-per-unit constants, `timespec_to_nsec`, `nsec_to_timespec`, and `now(clockid_t)`. `now` wraps `clock_gettime` and returns nanoseconds.

Control flow/state: no persistent state. The conversion helpers are arithmetic-only and expect values that fit in `uint64_t`/`time_t` fields.

Dependencies/integration: included by utilities, notify-wait, and signal/poll code that computes deadlines.

Risks/test signals: overflow at extreme timestamps and platform `time_t` size are the main portability risks. Inline assertions make clock failures fatal in callers using `now`.

Source research group: `subset-b-009122`.
