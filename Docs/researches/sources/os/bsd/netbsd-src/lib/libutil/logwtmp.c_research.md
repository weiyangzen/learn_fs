# File Research: sources/os/bsd/netbsd-src/lib/libutil/logwtmp.c

## Purpose
Appends a legacy `wtmp` record.

## Key Details
- Opens `_PATH_WTMP` append-only.
- Fills `ut_line`, `ut_name`, `ut_host`, and `ut_time`.
- If write is short, truncates back to the prior file size.

## Dependencies and Role
- Legacy login history writer.
