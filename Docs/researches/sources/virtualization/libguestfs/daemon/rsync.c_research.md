# File Research: sources/virtualization/libguestfs/daemon/rsync.c

Rsync wrapper for guest-local and remote sync.

Important behavior:
- Optgroup availability checks `rsync`.
- Shared helper builds `rsync` argv with optional `--archive` and `--delete`.
- `do_rsync` sysroot-prefixes both source and destination.
- `do_rsync_in` uses remote source to sysroot destination.
- `do_rsync_out` uses sysroot source to remote destination.

Filesystem relevance: bulk tree synchronization into, out of, or within mounted guest filesystems.
