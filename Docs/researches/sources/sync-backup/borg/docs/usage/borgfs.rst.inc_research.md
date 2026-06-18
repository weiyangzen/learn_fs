# sources/sync-backup/borg/docs/usage/borgfs.rst.inc

Purpose: generated reference for `borg borgfs`, a compatibility wrapper for mounting repositories or archives as FUSE filesystems.

Important APIs and control flow: command accepts `REPOSITORY_OR_ARCHIVE`, `MOUNTPOINT`, optional `PATH` selectors, `--foreground`, `-o` mount options, archive filters for repository mounts, exclude/pattern filters, and `--strip-components`. It delegates conceptually to `borg mount`.

State and persistence: creates a live FUSE mount and may daemonize. It does not modify archive contents, but kernel mount state persists until unmounted.

Dependencies and integration points: depends on FUSE implementation selection, fstab integration (`fuse.borgfs`), archive filtering, pattern matching, and `BORG_MOUNT_DATA_CACHE_ENTRIES` chunk cache tuning.

Risks: daemon crashes do not auto-unmount to avoid accidental data deletion by tools observing an empty mount. Damaged files return EIO unless `allow_damaged_files` is set. Versioned repository view is experimental.

Test signals: mount/unmount smoke tests for foreground and background modes, option passing through `-o`, path filtering, damaged-file behavior, and fstab wrapper compatibility.
