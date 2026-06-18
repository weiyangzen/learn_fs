# File Research: sources/os/bsd/netbsd-src/lib/libutil/ttyaction.c

## Purpose
Runs configured commands for matching tty/action/user events.

## Key Details
- Reads `/etc/ttyaction` by default.
- Strips leading `/dev/` from tty names.
- Matches tty and action fields using `fnmatch`.
- Executes matching command through `/bin/sh -c`.
- Provides environment variables `PATH`, `TTY`, `ACT`, and `USER`.
- Waits for each child and returns last status.

## Dependencies and Role
- Login/session hook mechanism based on filesystem configuration.
