# File Research: sources/os/plan9/plan9/sys/src/cmd/upas/fs/readdir.c

## Purpose
Tiny diagnostic program that opens `/mail/fs`, calls `dirread`, and prints directory entry names.

## Behavior
It loops over `dirread(fd, &d, sizeof(d))`, prints each `Dir.name`, and then prints the final read count.

## Dependencies
Plan 9 libc `open`, `dirread`, `print`.

## Risks / Notes
No error handling for failed `open`; likely an ad hoc test utility.
