# File Research: sources/os/bsd/freebsd-src/sbin/dump/optr.c

Operator interaction and status reporting support for `dump`.

Key responsibilities:
- `query()` asks yes/no questions on `/dev/tty`, periodically reprinting prompts through `SIGALRM`.
- `alarmcatch()` handles repeated attention prompts and optional operator broadcast mode.
- `interrupt()` asks whether to abort after `SIGINT`.
- `broadcast()` sends messages to the operator group through `wall -g operator`.
- `timeest()` computes percent complete and estimated finish time from `blockswritten`, `tapesize`, and elapsed write time.
- `infosch()` forces the next progress report.
- `msg()`, `msgtail()`, and `quit()` implement dump-specific diagnostic formatting and last-message tracking.
- `dump_getfstab()`, `fstabsearch()`, and `allocfsent()` build and search a UFS-only fstab table.
- `lastdump()` implements `dump -w` and `dump -W`.

Important data:
- `lastmsg`: retained for broadcast repetition.
- `timeout` and `attnmessage`: query prompt state.
- `tschedule`: next progress-report time.
- SLIST `table`: copied fstab entries used by dump lookup and lastdump.

Notable behavior:
- Query prompt repeats every 120 seconds.
- With `notify`, attention messages are sent to users in group `operator`.
- `lastdump()` sorts dumpdates by filesystem name and newest dump date before reporting.

Risks and constraints:
- Uses terminal interaction, alarms, and process title changes; behavior is intentionally operator-centric.
- `lastdump()` mutates the string returned by `ctime()` by truncating seconds/year display.
- `datesort()` subtracts `time_t` values into an `int`, which is historically common but width-sensitive.
