# sources/sync-backup/borg/docs/usage/mount.rst.inc

Purpose: Documents `borg mount`, which exposes a repository or archive as a FUSE filesystem for browsing/restoring files.

Important APIs/types/functions: CLI contract is `borg [common options] mount [options] MOUNTPOINT [PATH...]`. Important options include `--foreground`, `-o` mount options, `--numeric-ids`, archive filters, include/exclude patterns, and `--strip-components`. Borg-specific mount options include `versions`, `allow_damaged_files`, `ignore_permissions`, `uid`, and `gid`.

Control flow: Runtime opens the repository/archive, applies archive/path filters, constructs a FUSE view, daemonizes unless `--foreground` is used, and serves file metadata/data on demand. Whole-repository mounts lazily load archive directory structures when entered.

State and persistence: Intended repository state is read-only, but it creates a live mount process and kernel/user-space FUSE state at `MOUNTPOINT`. It may cache data chunks, controlled by `BORG_MOUNT_DATA_CACHE_ENTRIES`.

Dependencies and integration points: Depends on optional FUSE backends (`llfuse`, `pyfuse3`, or `mfusepy` per project extras), system FUSE configuration, `borgfs` wrapper, and `umount`. It integrates with archive filters and extraction semantics.

Risks: Symlinks are restored as-is, so following symlinks from a mount can escape the mount point. ACLs and special flags are not supported. Daemon crashes do not auto-unmount to avoid causing tools like rsync to delete data.

Test signals: Requires FUSE-enabled integration tests. Cover foreground/background behavior, uid/gid and numeric mapping, damaged-file handling, versioned repository view, path filtering, and unmount behavior.
