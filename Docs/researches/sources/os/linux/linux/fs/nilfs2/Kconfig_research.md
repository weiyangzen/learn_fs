# File Research: sources/os/linux/linux/fs/nilfs2/Kconfig

`Kconfig` declares `CONFIG_NILFS2_FS`, a tristate option named “NILFS2 file system support”. It selects `BUFFER_HEAD`, `CRC32`, and `LEGACY_DIRECT_IO`.

The help text describes NILFS2 as a log-structured filesystem with continuous snapshotting, checkpoint creation every few seconds or on synchronous writes, promotion of checkpoints into long-lived read-only snapshots, crash-consistent recovery, and concurrent read-only snapshot mounts for online backup.

The help also records feature limitations in this tree: atime, extended attributes, and POSIX ACLs are not supported yet. When built as a module, the module name is `nilfs2`; the default recommendation is `N` if unsure.
