# File Research: sources/os/plan9/plan9/sys/src/cmd/dial/at.c

This file implements a small AT-command driver used by dial scripts.

Key behaviors:
- Usage: `at [-q] [-t seconds] command`.
- For each command argument, sends `at<command>\r` to stdout one byte at a time with 100 ms pacing.
- Reads modem response lines from stdin using `readln()`, ignoring carriage returns.
- Recognizes success responses `ok\n` and `connect\n`.
- Recognizes failure responses such as `no carrier`, `no dialtone`, `error`, `busy`, `no answer`, `delayed`, and `blacklisted`.
- Mirrors modem output to `/dev/cons` unless `-q` is set.
- Default timeout is 2 minutes for dial commands beginning with `d`/`D`, otherwise 5 seconds.

Notable implementation details:
- `writewithoutcr()` strips carriage returns when echoing to console.
- Responses are compared case-insensitively.
- An alarm bounds response waiting.
