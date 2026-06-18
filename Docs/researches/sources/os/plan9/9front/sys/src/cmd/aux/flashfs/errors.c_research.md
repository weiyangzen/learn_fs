# File Research: sources/os/plan9/9front/sys/src/cmd/aux/flashfs/errors.c

Role: Shared flashfs error string definitions.

Contents:
- Defines constant error strings for non-empty directory deletion, existing file, non-existent file, directory/file type mismatches, permission denied, and read-only filesystem.

Use:
- Returned by flashfs entry and request operations through 9P `respond`.
