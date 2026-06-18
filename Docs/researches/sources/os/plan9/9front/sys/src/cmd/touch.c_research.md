# File Research: sources/os/plan9/9front/sys/src/cmd/touch.c

Read completely: 65 lines, 960 bytes.

Plan 9 `touch` implementation. It updates file modification time through `dirwstat`; if that fails and `-c` is not set, it creates the file with mode `0666` and sets its mtime through `dirfwstat`.

Key behavior:
- `-t time` sets the timestamp with `strtoul`.
- `-c` suppresses creation but still reports a failed `wstat`.
- Processes all path arguments and exits `"touch"` if any failed.

Dependencies:
- Uses `Dir`, `nulldir`, `dirwstat`, `create`, `dirfwstat`, and `time`.

Reliability notes:
- It sets only `mtime`; it does not attempt POSIX-style access-time preservation.
- Creation uses `OREAD|OEXCL`, so existing-file races fail cleanly.
