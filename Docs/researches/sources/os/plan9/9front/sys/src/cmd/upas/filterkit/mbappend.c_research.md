# File Research: sources/os/plan9/9front/sys/src/cmd/upas/filterkit/mbappend.c

This command appends stdin or listed files to a mailbox/folder owned by the current user.

Key behavior:
- Usage: `mbappend [-t time] [-f from] mbox [file ...]`.
- Resolves the target with `foldername(from, getuser(), mb)`.
- Calls `fappendfolder` with provided timestamp and optional from string.
- Logs each append through syslog and exits `fail` on append error.
- With no files, appends stdin; otherwise opens each file and appends it.

Integration and risks:
- The first argument to `foldername` is named `from` in this command but is the `mb` base parameter in common folder code; that naming is confusing and should be traced carefully when modifying.
