# File Research: sources/virtualization/guestfs-tools/filesystems/utils.h

Header for shared filesystem utility helpers.

Exports:
- `const char *get_filesystem_version(guestfs_h *g, const char *dev, const char *fs_type);`

Contract:
- Currently intended for XFS version reporting.
- May return `NULL` if no known version can be determined.

Research relevance: public local interface between `filesystems`, `inspector`, and the shared utility implementation.
