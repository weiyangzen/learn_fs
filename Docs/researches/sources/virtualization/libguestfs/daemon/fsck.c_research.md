# File Research: sources/virtualization/libguestfs/daemon/fsck.c

Thin wrapper for `fsck`.

Important behavior:
- `do_fsck(fstype, device)` runs `fsck -a -t <fstype> <device>` via `commandr`.
- Returns the fsck process status rather than only success/failure.
- Command execution failure reports captured stderr.

Filesystem relevance: exposes filesystem repair/check exit status through the daemon API.
