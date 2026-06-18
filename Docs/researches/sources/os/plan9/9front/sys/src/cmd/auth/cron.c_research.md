# File Research: sources/os/plan9/9front/sys/src/cmd/auth/cron.c

Plan 9 cron daemon for per-user scheduled jobs stored under `/cron`.

Key responsibilities:
- Parses `/cron/<user>/cron` entries with minute/hour/monthday/month/weekday/host/command fields.
- Watches each user's cron file by Qid and reloads jobs when the file changes.
- Enforces that `/cron/<user>` is owned by the same user name.
- Runs jobs locally through `rc -lc` or remotely through `/bin/rx`.
- Creates per-user cron directories/files with `-c`.
- Maintains a `/cron/lock` exclusive file to prevent multiple daemon instances.
- Handles time jumps by adapting backward jumps and capping forward catch-up to one day.
- Uses kernel uid capabilities through `/dev/caphash` and `/dev/capuse` to become the target user before running jobs.

Dependencies:
- Uses Plan 9 auth command helpers, syslog, `/cron`, `newns`, `rx`, `/dev/caphash`, `/dev/capuse`, and `/dev/null`.

Notable risks:
- Command execution is intentionally shell-based and wrapped as `exec rc -c '...'`, with quote escaping.
- Job ownership validation is important because jobs run after uid changes.
- Long time jumps can cause many missed-minute jobs to run in one pass, bounded to one day.
