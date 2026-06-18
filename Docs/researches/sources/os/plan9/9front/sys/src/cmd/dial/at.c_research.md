# File Research: sources/os/plan9/9front/sys/src/cmd/dial/at.c

Purpose: Sends modem AT commands over stdin/stdout and waits for recognized responses.

Key behavior:
- Options: `-q` quiet, `-t seconds` timeout.
- For each command argument, writes `at<cmd>\r` slowly, one byte every 100 ms.
- Default timeout is 5 seconds, except dial commands starting with `d`/`D` get 2 minutes.
- Reads response lines without carriage returns.
- Echoes modem output to `/dev/cons` unless quiet.
- Recognizes successful responses `ok` and `connect`; failures include `no carrier`, `no dialtone`, `error`, `busy`, `no answer`, `delayed`, and `blacklisted`.

Notable details:
- Matching is case-insensitive via `cistrstr()`.
- `writewithoutcr()` strips carriage returns when echoing.
