# File Research: sources/os/bsd/netbsd-src/lib/libutil/getmntopts.c

## Purpose
Parses comma-separated mount options into flag sets and option arguments.

## Key Details
- `getmntopts` tokenizes options, supports `no` prefixes, and handles `key=value` arguments.
- Uses a caller-provided `struct mntopt` table.
- Updates primary or alternate flag pointers depending on `m_altloc`.
- `getmntoptstr` returns saved argument text for an option.
- `getmntoptnum` converts an option argument to `long`.
- `freemntopts` frees parser state.
- Global `getmnt_silent` changes unsupported-option behavior from fatal `errx` to `NULL`/`-1`.

## Dependencies and Role
- Directly relevant to filesystem mount command implementations.
