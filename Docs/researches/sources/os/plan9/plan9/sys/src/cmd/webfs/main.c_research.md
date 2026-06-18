# File Research: sources/os/plan9/plan9/sys/src/cmd/webfs/main.c

This is the `webfs` server entry point.

Defaults:
- Cookie file: `$home/lib/webcookies` unless overridden.
- Mount point: `/mnt/web`.
- Global controls: accept cookies on, send cookies on, redirect limit 10, user-agent `webfs/2.0 (plan 9)`.

Options:
- `-d` enables paranoid/antagonistic pool flags.
- `-D` increments `chatty9p`.
- `-c` cookie file.
- `-m` mount point.
- `-s` service name.

Startup flow:
- Calls `quotefmtinstall`.
- Duplicates default user-agent.
- Initializes plumbing, cookies, URL regexps, and filesystem channels/thread.
- Posts the 9P server with `threadpostmountsrv`.

Role:
- Wires together the independent webfs subsystems into a mounted 9P service.
