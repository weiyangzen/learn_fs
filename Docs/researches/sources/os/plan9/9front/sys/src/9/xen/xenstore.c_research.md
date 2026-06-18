# File Research: sources/os/plan9/9front/sys/src/9/xen/xenstore.c

Purpose: Small Plan 9 user-space Xenstore command-line client.

Key behavior:
- Implements Xenstore wire message header `xsd_sockmsg` and command enum.
- `xscmd` sends one request and reads one response using a static 512-byte buffer.
- Commands: read, list directory, mkdir, delete, write, and watch.
- Binds `#x` onto `/dev` if `/dev/xenstore` is missing.
- Watch mode subscribes through `/dev/xenstore`, then reads events from `/dev/xenwatch`.

Integration notes: Talks to Plan 9 Xen device files rather than directly to Xen shared pages.

Risk/attention points: The static buffer bounds are not checked against path/value/response sizes. It prints response header diagnostics to fd 2 for every command.
