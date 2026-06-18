# sources/security-integrity/audit-userspace/audisp/plugins/ids/timer-services.c

Purpose: schedules and executes delayed IDS undo operations, currently account unlock and IP unblock.

Important APIs and data: implements `init_timer_services`, `do_timer_services`, `add_timer_job`, and `shutdown_timer_services`. Uses a static `nvlist jobs` and monotonic-ish static `now`.

Control flow: initialization creates the list and captures current time. Each service tick handles dump/reload signals, advances `now` by the caller interval with drift correction, then repeatedly finds expired jobs and runs the matching reaction before deleting the job. New jobs store `time(NULL) + length`.

State and persistence: timer jobs are in memory only; a comment notes they should probably be persistent to survive restart.

Dependencies and integration: depends on `nvpair.c`, `reactions.c`, `origin.c`, audit response logging, global signal flags, and IDS output/reload functions.

Risks: delayed undo is lost on process restart, so timed locks/blocks can remain active externally. The internal clock is adjusted by interval and corrected only when drift exceeds the interval.

Test signals: schedule unlock/unblock jobs, advance service intervals, verify action execution and deletion. Restart persistence is explicitly absent.
