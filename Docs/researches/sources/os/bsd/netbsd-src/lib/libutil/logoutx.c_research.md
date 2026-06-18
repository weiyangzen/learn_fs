# File Research: sources/os/bsd/netbsd-src/lib/libutil/logoutx.c

## Purpose
Updates a `utmpx` entry to represent logout/session termination.

## Key Details
- Looks up the line with `getutxline`.
- Sets `ut_type`.
- Records exit status and termination signal when applicable.
- Updates timestamp and writes with `pututxline`.
- Calls `endutxent`.

## Dependencies and Role
- Extended login accounting cleanup.
