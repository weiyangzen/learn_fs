# File Research: sources/os/plan9/9front/sys/src/cmd/dial/drain.c

Purpose: Drains pending input briefly.

Key behavior:
- Sets a 100 ms alarm.
- Reads and discards stdin until read returns non-positive.
- Clears alarm and exits.

Notable details:
- `ding()` is defined to continue on alarm notes, but `main()` does not call `notify(ding)` in this file as read, so alarm behavior relies on default note handling unless installed elsewhere.
