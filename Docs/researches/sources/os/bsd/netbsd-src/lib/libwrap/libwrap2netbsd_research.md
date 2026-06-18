# File Research: sources/os/bsd/netbsd-src/lib/libwrap/libwrap2netbsd

## Purpose
Shell import helper for converting an upstream tcp_wrappers source tree into NetBSD’s `libwrap` tree layout.

## Key Details
- Requires two arguments: source and destination.
- Deletes and recreates `$dest/libwrap`.
- Copies selected source files, manpages, headers, and miscellaneous files using `pax`.
- Does not transform contents beyond selecting files.

## Dependencies and Role
- Maintenance/import script, not part of the built library.
