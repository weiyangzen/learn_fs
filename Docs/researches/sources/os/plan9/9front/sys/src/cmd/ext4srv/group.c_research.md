# File Research: sources/os/plan9/9front/sys/src/cmd/ext4srv/group.c

Parser and lookup helpers for the ext4srv user/group table used by permission checks.

Key behavior:
- `loadgroups` duplicates the raw group file, parses colon-separated records, validates numeric IDs, appends `Group` records, and parses comma-separated member names.
- After parsing all records, member names are resolved to numeric IDs with `findgroup`.
- `freegroups` releases each group's member array plus the group array and raw backing string.
- `findgroup` looks up by name and optionally returns the numeric ID, using `~0` when not found.
- `findgroupid` looks up by numeric ID.
- `ingroup` checks direct identity or membership in a group's resolved member list.

Notable dependencies:
- Uses Plan 9 libc helpers: `getfields`, `strtoll`, `werrstr`, `strdup`, and allocation routines.
- Public structs and prototypes are in `group.h`.

Research notes:
- Group and member names point into `Groups.raw`, so the duplicated raw string must outlive all `Group` records.
- Missing member names resolve to ID `~0`; there is no hard failure for unresolved members in the second pass.
- The parser expects at least three colon fields and, if present, uses the fourth field for members.
