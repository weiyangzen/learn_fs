# File Research: sources/virtualization/libguestfs/daemon/devsparts.c

Implements listing of libguestfs disk labels.

Key points:
- Reads `/dev/disk/guestfs`.
- Missing directory is treated as an empty list, usually meaning no labels.
- For each non-dot entry, resolves the symlink with `realpath`.
- Returns alternating label and raw device path strings.
- Carefully handles directory close and `readdir` errors.
