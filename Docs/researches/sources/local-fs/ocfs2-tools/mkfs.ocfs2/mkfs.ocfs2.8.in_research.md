# File Research: sources/local-fs/ocfs2-tools/mkfs.ocfs2/mkfs.ocfs2.8.in

Manual page template for `mkfs.ocfs2`.

Key contents:
- Synopsis and purpose of creating OCFS2 filesystems.
- Documents options for block size, cluster size, force, journal options, label, mount mode, node slots, filesystem type, feature sets, cluster stack/name, global heartbeat, discard, dry-run, quiet, UUID, verbose, version, and explicit block count.
- Explains feature levels: `max-compat`, `default`, `max-features`.
- Lists individual features and their semantics.
- Provides feature compatibility table by kernel/tool version.
- Provides feature bit-value table for debugging unsupported-feature mount failures.

Research notes:
- The man page states that default feature level enables sparse, unwritten, inline-data, xattr, indexed-dirs, discontig-bg, refcount, extended-slotmap, and clusterinfo.
- It warns strongly against manually reusing UUIDs.
- The `--no-backup-super` option is documented as deprecated in favor of `--fs-features=nobackup-super`.
