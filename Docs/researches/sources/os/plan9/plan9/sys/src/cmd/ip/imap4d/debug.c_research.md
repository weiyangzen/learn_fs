# File Research: sources/os/plan9/plan9/sys/src/cmd/ip/imap4d/debug.c

Debugging helpers for `imap4d`. `debuglog` writes optional per-user diagnostics to `/sys/log/imap4d`; `boxVerify` checks message sequence, UID, recent count, and mailbox counters; `openfiles` dumps open file descriptors; and `ls` recursively-style lists directory entries for inspection.
