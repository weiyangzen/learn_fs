# File Research: sources/virtualization/libguestfs/daemon/umask.c

## Role
Implements daemon actions for setting and reading the process umask.

## Main Operations
- `do_umask()` validates the mask is between `0000` and `0777`, calls `umask()`, and returns the previous value.
- `do_get_umask()` reads the current mask by temporarily setting it to `022`, then restores the previous value.

## Filesystem/Storage Relevance
The daemon umask influences default permissions for files and directories created during guest filesystem operations.
