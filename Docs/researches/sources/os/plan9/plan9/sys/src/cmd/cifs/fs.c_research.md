# File Research: sources/os/plan9/plan9/sys/src/cmd/cifs/fs.c

Generates textual diagnostic/info files exposed by the CIFS 9P root. Functions format shares, open files, connection/capability/security state, active sessions, DFS roots, users, groups, domains, and workstations.

Most data comes from RAP calls over `IPC$`; DFS root data comes from Trans2 DFS referrals. The code frees nested strings returned by RAP helpers as it formats them. `period` formats session durations. These functions are registered in `info.c`.
