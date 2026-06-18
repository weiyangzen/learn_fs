# File Research: sources/os/bsd/netbsd-src/lib/libutil/logout.c

## Purpose
Marks a legacy `utmp` line as logged out.

## Key Details
- Opens `_PATH_UTMP` read/write.
- Searches for matching `ut_line` with nonempty `ut_name`.
- Clears `ut_name` and `ut_host`.
- Updates `ut_time`.
- Rewrites the record in place.
- Returns `1` if a record was updated, otherwise `0`.

## Dependencies and Role
- Legacy login accounting cleanup.
