# File Research: sources/os/bsd/netbsd-src/lib/libutil/getfsspecname.c

## Purpose
Resolves filesystem specifier names, especially `NAME=` wedge names and `ROOT.` aliases, to device paths.

## Key Details
- `ROOT.` expands using `kern.root_device` sysctl into `/dev/<root_device>...`.
- Non-`NAME=` inputs are returned unchanged, except compatibility logic may treat busy raw disk opens as wedge label lookups.
- For `NAME=`, unvises the name, scans `hw.disknames`, opens `dk` devices, and checks `DIOCGWEDGEINFO`.
- Converts raw `rdk` paths to cooked `dk` paths by removing the `r`.
- Returns `NULL` and writes diagnostic text into `buf` on failures such as no match or sysctl errors.

## Dependencies and Role
- Filesystem mount helper for symbolic wedge/root device names.
