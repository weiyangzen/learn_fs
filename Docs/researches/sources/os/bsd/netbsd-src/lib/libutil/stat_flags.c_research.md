# File Research: sources/os/bsd/netbsd-src/lib/libutil/stat_flags.c

## Purpose
Converts BSD file flags between bitmasks and strings.

## Key Details
- `flags_to_string` emits comma-separated names such as `uappnd`, `uchg`, `nodump`, `opaque`, `sappnd`, `arch`, `schg`, and optionally `snap`.
- Returns a duplicated default string if no flags are set.
- `string_to_flags` parses comma/space-separated tokens into set and clear masks.
- Supports `no` prefixes and aliases such as `uappend`, `simmutable`, and `dump`.

## Dependencies and Role
- Filesystem metadata utility used by tools that expose inode flags.
