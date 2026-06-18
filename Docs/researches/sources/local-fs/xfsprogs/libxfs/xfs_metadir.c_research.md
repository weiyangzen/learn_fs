# File Research: sources/local-fs/xfsprogs/libxfs/xfs_metadir.c

## Role

This file implements the metadata directory tree abstraction. It supports looking up, loading, creating, linking, committing, canceling, and making directories for metadata inodes stored under a special metadata directory tree.

It does not manage the legacy realtime bitmap/summary or quota inode locations; newer metadata inodes should go through the metadir/metafile APIs.

## Lookup And Load

`xfs_metadir_set_xname` builds an `xfs_name` from a path component and expected file type.

`xfs_metadir_lookup` looks up a component in a metadata directory using directory da args. It requires an exclusive ILOCK on the parent, verifies the parent is a directory, rejects shutdown, validates the returned inode number, checks file type when requested, marks the metadir sick on corruption, and returns the inode number.

`xfs_metadir_load` locks the parent, looks up the component, unlocks, and loads the inode with `xfs_trans_metafile_iget`, validating the expected metafile type.

## Update Lifecycle

`struct xfs_metadir_update` is initialized by callers and passed through start, mutate, and commit/cancel operations.

`xfs_metadir_teardown` releases parent pointer args and unlocks child/parent inode locks as needed.

`xfs_metadir_start_create` allocates parent-pointer context, allocates a create transaction, and locks the parent directory with parent lock ordering.

`xfs_metadir_commit` commits the transaction and tears down resources.

`xfs_metadir_cancel` cancels the transaction and tears down resources.

## Create And Link

`xfs_metadir_create` verifies the final component does not already exist, allocates and creates an inode, marks it with `xfs_metafile_set_iflag`, joins the parent directory after possible transaction rolling, and creates the directory entry. It returns the newly created inode locked in the update structure.

The non-kernel `xfs_metadir_start_link` and `xfs_metadir_link` paths link an existing metadata inode into the metadir tree. They reserve directory link space, lock parent and child, require reservation space, reject duplicate final components, and add the directory entry.

`xfs_metadir_mkdir` wraps create-start, directory create, commit, finish setup, and error cleanup for a metadata subdirectory.

## Invariants

- Metadata directory tree inodes require ILOCK synchronization; IOLOCK/MMAPLOCK are unnecessary because metadata files are not exposed to userspace.
- Created metadata files are marked with the metadata inode flag and mandatory metadata flags.
- Parent pointers are prepared and passed to directory updates when the feature is enabled.
- Files in the metadata directory tree currently cannot be unlinked here.
- Metadir feature must be enabled for create/link operations.

## Dependencies

This file integrates with directory lookup/add/create helpers, inode allocation and creation, transaction reservations, parent pointer update contexts, metafile flagging, health marking, and mount feature predicates.

## Research Notes

The transaction lifecycle is the main usage contract: callers must commit or cancel every started update. `xfs_metadir_create` can return an inode even on error, so callers must finish setup and release it during cleanup.
