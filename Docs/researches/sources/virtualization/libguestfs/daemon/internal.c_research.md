# File Research: sources/virtualization/libguestfs/daemon/internal.c

Internal daemon-only lifecycle actions.

Important behavior:
- `do_internal_autosync` conditionally calls `do_umount_all` if `autosync_umount` is set, then calls `sync_disks`.
- `do_internal_exit` replies first, then exits successfully; intended for valgrind daemon runs.

Filesystem relevance: final synchronization and unmount behavior before handle shutdown.
